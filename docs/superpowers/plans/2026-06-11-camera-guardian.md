# Camera Guardian Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Monitor de câmera macOS que dispara um overlay vermelho fullscreen ("SAI DAI VAGABUNDO") quando um rosto desconhecido aparece e o limpa quando o dono reaparece.

**Architecture:** Thread de fundo lê a câmera, reconhece rostos (`face_recognition`) e alimenta uma máquina de estados pura com debounce. A main thread roda um overlay Tkinter que faz polling do estado e mostra/esconde a janela vermelha.

**Tech Stack:** Python 3, OpenCV (`opencv-python`), `face_recognition` (dlib), Tkinter (stdlib), pytest.

---

## File Structure

| Arquivo | Responsabilidade |
|---|---|
| `config.py` | Constantes ajustáveis (tolerance, debounce, downscale, textos) |
| `state.py` | Máquina de estados pura (`GuardianState`) — **ponto de contribuição do Gab** |
| `detector.py` | Câmera + reconhecimento; por quadro retorna `(known, unknown)` |
| `capture.py` | Ferramenta manual: tira fotos do dono pela webcam |
| `enroll.py` | Lê `known_faces/*` → embeddings → `encodings.pkl` |
| `overlay.py` | Janela Tkinter fullscreen vermelha; show/hide por polling |
| `guardian.py` | Orquestra detector(thread) → state → overlay(main) |
| `tests/test_state.py` | Testes unitários puros da máquina de estados |
| `requirements.txt` | Dependências |

**Ambiente (rodar uma vez, antes da Task 1):**

```bash
cd /Users/gab/repo/camera-guardian
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -U pip pytest
```

> Tkinter precisa estar disponível. Em Python do python.org já vem. Em Homebrew: `brew install python-tk`. Verifique com `python -c "import tkinter; print('ok')"`.

---

## Task 1: config.py

**Files:**
- Create: `config.py`

- [ ] **Step 1: Criar o arquivo de configuração**

```python
# config.py — tunables do Camera Guardian

TOLERANCE = 0.6          # distância máx. p/ considerar KNOWN (menor = mais rígido)
DEBOUNCE_FRAMES = 3      # quadros consecutivos p/ trocar de estado
DOWNSCALE = 0.25         # fator de redução do quadro antes da detecção
DETECTION_MODEL = "hog"  # "hog" (CPU, rápido) ou "cnn" (GPU, preciso)

CAMERA_INDEX = 0
POLL_MS = 100            # intervalo de polling do overlay (ms)

ENCODINGS_PATH = "encodings.pkl"
KNOWN_FACES_DIR = "known_faces"

ALERT_TEXT = "SAI DAI VAGABUNDO"
ALERT_BG = "#cc0000"     # vermelho
ALERT_FG = "#ffffff"     # texto branco
ALERT_FONT_SIZE = 120
```

- [ ] **Step 2: Verificar import**

Run: `python -c "import config; print(config.ALERT_TEXT)"`
Expected: `SAI DAI VAGABUNDO`

- [ ] **Step 3: Commit**

```bash
git add config.py
git commit -m "feat: config com tunables do guardian"
```

---

## Task 2: state.py — máquina de estados (TDD)

> **★ Ponto de contribuição do Gab.** O Step 3 (a lógica do `update`) é o coração do guardião — 5-10 linhas que definem todo o comportamento. Durante a execução, escreva você primeiro; a referência abaixo é o gabarito pra conferir.

**Files:**
- Test: `tests/test_state.py`
- Create: `state.py`

- [ ] **Step 1: Escrever os testes que falham**

```python
# tests/test_state.py
from state import GuardianState


def test_comeca_limpo():
    s = GuardianState(debounce_frames=3)
    assert s.alert_active is False


def test_desconhecido_dispara_apos_debounce():
    s = GuardianState(debounce_frames=3)
    assert s.update(known=0, unknown=1) is False   # quadro 1
    assert s.update(known=0, unknown=1) is False   # quadro 2
    assert s.update(known=0, unknown=1) is True    # quadro 3 -> dispara


def test_desconhecido_tem_prioridade_sobre_dono():
    s = GuardianState(debounce_frames=1)
    # dono + intruso no mesmo quadro -> intruso ganha
    assert s.update(known=1, unknown=1) is True


def test_dono_limpa_apos_debounce():
    s = GuardianState(debounce_frames=2, start_alert=True)
    assert s.update(known=1, unknown=0) is True    # quadro 1 (ainda alerta)
    assert s.update(known=1, unknown=0) is False   # quadro 2 -> limpa


def test_quadro_vazio_mantem_estado_de_alerta():
    s = GuardianState(debounce_frames=1, start_alert=True)
    # ninguém no quadro: continua vermelho até o dono voltar
    assert s.update(known=0, unknown=0) is True
    assert s.update(known=0, unknown=0) is True


def test_quadro_vazio_mantem_estado_limpo():
    s = GuardianState(debounce_frames=1, start_alert=False)
    assert s.update(known=0, unknown=0) is False


def test_quadro_isolado_nao_troca_estado():
    s = GuardianState(debounce_frames=3)
    s.update(known=0, unknown=1)   # 1 quadro rumo a alerta
    s.update(known=1, unknown=0)   # dono aparece -> reseta o streak
    assert s.update(known=0, unknown=1) is False  # recomeça do zero, não dispara


def test_intruso_sai_continua_vermelho_ate_dono_voltar():
    s = GuardianState(debounce_frames=1)
    assert s.update(known=0, unknown=1) is True    # intruso dispara
    assert s.update(known=0, unknown=0) is True    # intruso saiu, vazio -> latch
    assert s.update(known=1, unknown=0) is False   # dono volta -> limpa
```

- [ ] **Step 2: Rodar os testes e ver falhar**

Run: `python -m pytest tests/test_state.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'state'`

- [ ] **Step 3: Implementar `state.py` (CONTRIBUIÇÃO DO GAB)**

Especificação do método `update(known, unknown) -> bool`:

1. Decide o `target` deste quadro: `unknown > 0` → `True`; senão `known > 0` → `False`; senão (vazio) → mantém `alert_active` atual (latch).
2. Se `target` == estado atual: reseta o contador de debounce, retorna o estado atual.
3. Se `target` difere: conta quadros consecutivos concordando com `target`; ao atingir `debounce_frames`, comita a troca.

Gabarito de referência:

```python
# state.py
class GuardianState:
    """Decisão pura: dadas as contagens de rostos por quadro, liga/desliga o alerta.

    Prioridade: UNKNOWN > KNOWN > (vazio = mantém estado / latch).
    Debounce: só troca após `debounce_frames` quadros consecutivos concordando.
    """

    def __init__(self, debounce_frames=3, start_alert=False):
        self.debounce_frames = debounce_frames
        self.alert_active = start_alert
        self._pending = start_alert
        self._count = 0

    def update(self, known, unknown):
        if unknown > 0:
            target = True
        elif known > 0:
            target = False
        else:
            target = self.alert_active  # quadro vazio: latch

        if target == self.alert_active:
            self._pending = target
            self._count = 0
            return self.alert_active

        if target == self._pending:
            self._count += 1
        else:
            self._pending = target
            self._count = 1

        if self._count >= self.debounce_frames:
            self.alert_active = target
            self._count = 0
        return self.alert_active
```

- [ ] **Step 4: Rodar os testes e ver passar**

Run: `python -m pytest tests/test_state.py -v`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add state.py tests/test_state.py
git commit -m "feat: máquina de estados do guardian com debounce (TDD)"
```

---

## Task 3: requirements.txt

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Criar requirements**

```text
opencv-python>=4.9
face_recognition>=1.3
numpy>=1.26
```

- [ ] **Step 2: Instalar (dlib compila — pode levar alguns minutos)**

Run: `source .venv/bin/activate && pip install -r requirements.txt`
Expected: instala sem erro. Se `dlib` falhar, instalar `cmake` antes: `pip install cmake` (ou `brew install cmake`).

- [ ] **Step 3: Verificar imports**

Run: `python -c "import cv2, face_recognition, numpy; print('deps ok')"`
Expected: `deps ok`

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: dependências (opencv, face_recognition, numpy)"
```

---

## Task 4: capture.py — tirar fotos do dono

**Files:**
- Create: `capture.py`

> Manual/smoke (precisa de webcam). Sem teste unitário.

- [ ] **Step 1: Implementar o capturador**

```python
# capture.py — tira fotos da webcam p/ enrollment. ESPAÇO=foto, Q=sair.
import os
import cv2
import config


def main():
    os.makedirs(config.KNOWN_FACES_DIR, exist_ok=True)
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        raise SystemExit(
            "Não consegui abrir a câmera. Libere Câmera pro Terminal em "
            "Ajustes do Sistema → Privacidade e Segurança → Câmera."
        )
    print("ESPAÇO = tirar foto | Q = sair")
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            continue
        cv2.imshow("Capture (ESPACO=foto, Q=sair)", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(" "):
            path = os.path.join(config.KNOWN_FACES_DIR, f"gab_{n:02d}.jpg")
            cv2.imwrite(path, frame)
            print(f"[salvo] {path}")
            n += 1
        elif key == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
    print(f"{n} foto(s) salvas em {config.KNOWN_FACES_DIR}/")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke test**

Run: `python capture.py`
Expected: abre janela da webcam; ESPAÇO salva `known_faces/gab_00.jpg`; Q fecha. Tire 3-5 fotos com ângulos/iluminação variados.

- [ ] **Step 3: Commit**

```bash
git add capture.py
git commit -m "feat: capture.py p/ tirar fotos de enrollment"
```

---

## Task 5: enroll.py — gerar encodings

**Files:**
- Create: `enroll.py`

- [ ] **Step 1: Implementar o enrollment**

```python
# enroll.py — lê known_faces/* → embeddings de 128d → encodings.pkl
import glob
import os
import pickle
import face_recognition
import config


def build_encodings(faces_dir, out_path):
    patterns = ("*.jpg", "*.jpeg", "*.png")
    paths = sorted(
        p for pat in patterns for p in glob.glob(os.path.join(faces_dir, pat))
    )
    if not paths:
        raise SystemExit(
            f"Sem fotos em {faces_dir}/. Rode `python capture.py` primeiro "
            f"ou coloque fotos suas (jpg/png) na pasta."
        )
    encodings = []
    for p in paths:
        img = face_recognition.load_image_file(p)
        encs = face_recognition.face_encodings(img)
        if not encs:
            print(f"[pula] nenhum rosto em {p}")
            continue
        encodings.append(encs[0])
        print(f"[ok] {p}")
    if not encodings:
        raise SystemExit("Nenhum rosto detectado nas fotos.")
    with open(out_path, "wb") as f:
        pickle.dump(encodings, f)
    print(f"Salvo {len(encodings)} encoding(s) em {out_path}")


if __name__ == "__main__":
    build_encodings(config.KNOWN_FACES_DIR, config.ENCODINGS_PATH)
```

- [ ] **Step 2: Smoke test**

Run: `python enroll.py`
Expected: imprime `[ok]` por foto e `Salvo N encoding(s) em encodings.pkl`. Cria `encodings.pkl`.

- [ ] **Step 3: Commit**

```bash
git add enroll.py
git commit -m "feat: enroll.py gera encodings.pkl das fotos do dono"
```

---

## Task 6: detector.py — câmera + reconhecimento

**Files:**
- Create: `detector.py`

> Lógica de hardware — smoke test manual.

- [ ] **Step 1: Implementar o detector**

```python
# detector.py — lê a câmera e classifica rostos como known/unknown por quadro.
import pickle
import cv2
import face_recognition


class Detector:
    def __init__(self, encodings_path, camera_index, downscale, model, tolerance):
        try:
            with open(encodings_path, "rb") as f:
                self.known = pickle.load(f)
        except FileNotFoundError:
            raise SystemExit(
                f"Sem {encodings_path}. Rode `python enroll.py` primeiro."
            )
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise SystemExit(
                "Não consegui abrir a câmera. Libere Câmera pro Terminal em "
                "Ajustes do Sistema → Privacidade e Segurança → Câmera."
            )
        self.downscale = downscale
        self.model = model
        self.tolerance = tolerance

    def read_counts(self):
        """Retorna (known, unknown) do quadro atual, ou None se a leitura falhar."""
        ok, frame = self.cap.read()
        if not ok:
            return None
        small = cv2.resize(frame, (0, 0), fx=self.downscale, fy=self.downscale)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model=self.model)
        encodings = face_recognition.face_encodings(rgb, locations)
        known = unknown = 0
        for enc in encodings:
            distances = face_recognition.face_distance(self.known, enc)
            if len(distances) and distances.min() <= self.tolerance:
                known += 1
            else:
                unknown += 1
        return known, unknown

    def release(self):
        self.cap.release()
```

- [ ] **Step 2: Smoke test (script temporário)**

Run:
```bash
python -c "
import config
from detector import Detector
d = Detector(config.ENCODINGS_PATH, config.CAMERA_INDEX, config.DOWNSCALE, config.DETECTION_MODEL, config.TOLERANCE)
for _ in range(30):
    print(d.read_counts())
d.release()
"
```
Expected: imprime tuplas `(known, unknown)`. Com sua cara na frente: `(1, 0)`. Com outra pessoa: `(0, 1)`.

- [ ] **Step 3: Commit**

```bash
git add detector.py
git commit -m "feat: detector de câmera + reconhecimento (known/unknown por quadro)"
```

---

## Task 7: overlay.py — janela vermelha fullscreen

**Files:**
- Create: `overlay.py`

> GUI — smoke test manual.

- [ ] **Step 1: Implementar o overlay**

```python
# overlay.py — janela Tkinter fullscreen vermelha; polling de um callback bool.
import tkinter as tk
import config


class Overlay:
    def __init__(self, get_alert, poll_ms):
        self.get_alert = get_alert  # callable() -> bool
        self.poll_ms = poll_ms
        self.root = tk.Tk()
        self.root.title("Camera Guardian")
        self.root.configure(bg=config.ALERT_BG)
        self.label = tk.Label(
            self.root,
            text=config.ALERT_TEXT,
            fg=config.ALERT_FG,
            bg=config.ALERT_BG,
            font=("Helvetica", config.ALERT_FONT_SIZE, "bold"),
            wraplength=1,
        )
        self.label.pack(expand=True, fill="both")
        # ESC esconde manualmente (failsafe durante testes)
        self.root.bind("<Escape>", lambda e: self._hide())
        self.root.withdraw()
        self._visible = False

    def _show(self):
        self.root.deiconify()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.label.config(wraplength=self.root.winfo_screenwidth() - 80)
        self.root.lift()
        self._visible = True

    def _hide(self):
        self.root.withdraw()
        self._visible = False

    def _poll(self):
        alert = self.get_alert()
        if alert and not self._visible:
            self._show()
        elif not alert and self._visible:
            self._hide()
        self.root.after(self.poll_ms, self._poll)

    def run(self):
        self.root.after(self.poll_ms, self._poll)
        self.root.mainloop()
```

- [ ] **Step 2: Smoke test (alterna sozinho 5s on/off)**

Run:
```bash
python -c "
import time, threading
import config
from overlay import Overlay
state = {'on': False}
def flip():
    while True:
        time.sleep(5); state['on'] = not state['on']
threading.Thread(target=flip, daemon=True).start()
Overlay(lambda: state['on'], config.POLL_MS).run()
"
```
Expected: a cada 5s a tela vira vermelha com "SAI DAI VAGABUNDO" e some. ESC esconde. Ctrl+C no terminal encerra.

- [ ] **Step 3: Commit**

```bash
git add overlay.py
git commit -m "feat: overlay Tkinter fullscreen vermelho"
```

---

## Task 8: guardian.py — orquestração

**Files:**
- Create: `guardian.py`

- [ ] **Step 1: Implementar o wiring**

```python
# guardian.py — detector(thread de fundo) → state → overlay(main thread).
import threading
import config
from detector import Detector
from state import GuardianState
from overlay import Overlay


def main():
    detector = Detector(
        config.ENCODINGS_PATH,
        config.CAMERA_INDEX,
        config.DOWNSCALE,
        config.DETECTION_MODEL,
        config.TOLERANCE,
    )
    state = GuardianState(debounce_frames=config.DEBOUNCE_FRAMES)
    stop = threading.Event()
    lock = threading.Lock()
    alert = {"value": False}

    def loop():
        while not stop.is_set():
            counts = detector.read_counts()
            if counts is None:
                continue
            known, unknown = counts
            active = state.update(known, unknown)
            with lock:
                alert["value"] = active

    worker = threading.Thread(target=loop, daemon=True)
    worker.start()

    def get_alert():
        with lock:
            return alert["value"]

    overlay = Overlay(get_alert, config.POLL_MS)
    try:
        overlay.run()
    finally:
        stop.set()
        detector.release()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Teste de integração (manual, end-to-end)**

Run: `python guardian.py`
Expected:
- Com sua cara na câmera → tela normal.
- Outra pessoa (ou foto de outra pessoa) entra no quadro → após ~3 quadros, tela fica vermelha "SAI DAI VAGABUNDO".
- Intruso sai, tela continua vermelha; sua cara reaparece → some.

- [ ] **Step 3: Commit**

```bash
git add guardian.py
git commit -m "feat: guardian orquestra detector + state + overlay"
```

---

## Task 9: README final + push

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Atualizar a seção de uso do README**

Confirmar que o bloco de setup reflete o fluxo real:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python capture.py    # tira fotos suas (ESPAÇO/Q)
python enroll.py     # gera encodings.pkl
python guardian.py   # liga o guardião
```

- [ ] **Step 2: Rodar a suíte de testes uma última vez**

Run: `python -m pytest -v`
Expected: PASS (8 passed)

- [ ] **Step 3: Commit e push**

```bash
git add README.md
git commit -m "docs: fluxo de uso completo no README"
git push
```

---

## Self-Review (cobertura do spec)

- ✅ Regra UNKNOWN > KNOWN > latch — `state.py` + testes (Task 2)
- ✅ Debounce N quadros — `state.py` + teste (Task 2)
- ✅ Reconhecimento por embedding + tolerance — `detector.py` (Task 6), `enroll.py` (Task 5)
- ✅ Overlay vermelho fullscreen show/hide — `overlay.py` (Task 7)
- ✅ Threading detector(bg) + overlay(main) — `guardian.py` (Task 8)
- ✅ Erros: sem câmera / sem encodings / quadro falho — `detector.py`/`capture.py` (Tasks 4, 6)
- ✅ Tunables — `config.py` (Task 1)
- ✅ Testes unitários puros da máquina de estados — Task 2
