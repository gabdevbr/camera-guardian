# Troubleshooting

Erros comuns + correções conhecidas. Complementa [`security.md`](security.md) (privacidade/biometria) e o [`CLAUDE.md`](../CLAUDE.md) (gotchas).

---

## Instalação / Ambiente

### `import tkinter` falha com `ModuleNotFoundError: No module named '_tkinter'`

O Python do Homebrew não vem com Tk. Instale o suporte e recrie a venv se preciso:

```bash
brew install python-tk@3.14          # ajuste pra sua versão de Python
```

### `face_recognition` reclama: `Please install face_recognition_models`

Na verdade o pacote está instalado, mas `face_recognition_models` importa `pkg_resources`, removido em `setuptools>=81` (afeta Python 3.14). Fix:

```bash
pip install "setuptools<81"
```

Já está fixado no [`requirements.txt`](../requirements.txt).

### Build do `dlib` demora / falha

`face_recognition` compila o `dlib` (alguns minutos). Se falhar por falta de compilador:

```bash
pip install cmake        # ou: brew install cmake
pip install -r requirements.txt
```

---

## Câmera

### Janela da webcam não abre / erro "Não consegui abrir a câmera"

Falta permissão de câmera pro terminal. Libere em **Ajustes do Sistema → Privacidade e Segurança → Câmera** e marque seu terminal. Depois rode de novo.

### ESPAÇO não tira foto no `capture.py`

O foco do teclado está no terminal, não na janela do OpenCV. **Clique na janela da câmera primeiro**, aí aperte **ESPAÇO** (ou **S**). O contador "Fotos salvas" na janela confirma. Sair com **Q** ou **ESC**.

---

## Testes

### `pytest` retorna "No tests collected" ou `ModuleNotFoundError: No module named 'state'`

Não há `conftest.py`/pacote, então a raiz precisa estar no path. Rode da raiz com:

```bash
PYTHONPATH=. python -m pytest tests/ -v
```

Se o hook RTK reescrever o comando e quebrar a coleta, use `rtk proxy python -m pytest tests/ -v`.

---

## Reconhecimento / Comportamento

### Dispara comigo (falso positivo)

O dono está sendo lido como desconhecido. Tente:
1. Recadastrar com mais fotos variando ângulo/luz (`python capture.py` → `python enroll.py`).
2. Afrouxar levemente o limiar em `config.py`: `TOLERANCE = 0.65`.

### Não dispara com estranhos / pisca demais

1. Apertar o limiar: `TOLERANCE = 0.5`.
2. Se o alerta "tremer" (liga/desliga), suba `DEBOUNCE_FRAMES = 5`.

### ⚠️ Burlam mostrando uma FOTO minha (impressa ou no celular)

**Não é bug — é limitação da v1.** O reconhecimento não detecta vivacidade (*liveness*), então uma foto do dono passa como o dono. Apertar `TOLERANCE` **não** resolve de forma confiável. A solução real é anti-spoofing (piscada/movimento, textura/moiré, challenge-response) — ver roadmap em [`security.md`](security.md#️-limitação-conhecida-spoofing-por-foto-sem-liveness). Até lá, trate o guardião como dissuasão/brincadeira, não controle de acesso.

---

## Overlay

### Não consigo sair do alerta vermelho fullscreen

**ESC** esconde a janela na hora (failsafe). Pra encerrar o processo, **Ctrl+C** no terminal, ou **Cmd+Tab** pra voltar ao terminal e matar.

---

## Diagnóstico rápido

```bash
source .venv/bin/activate
python -c "import cv2, face_recognition, numpy, tkinter; print('deps ok')"   # todas as libs
PYTHONPATH=. python -m pytest tests/ -v                                       # lógica ok
ls -la encodings.npy known_faces/                                            # cadastro feito?
```

Se nada acima ajudou: confira a permissão de câmera e recrie a venv (`rm -rf .venv && ./start.sh`).
