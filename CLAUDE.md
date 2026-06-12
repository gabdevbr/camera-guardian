# Camera Guardian — monitor de câmera macOS que dispara alerta vermelho com rosto desconhecido

> **Companion docs:** [`AGENTS.md`](./AGENTS.md) (regras de engenharia) · [`CHANGELOG.md`](./CHANGELOG.md) (histórico) · [`docs/security.md`](./docs/security.md) (privacidade/biometria) · [`docs/troubleshooting.md`](./docs/troubleshooting.md) (erros comuns) · [`README.md`](./README.md) (overview público). Design e plano em [`docs/superpowers/`](./docs/superpowers/). Este arquivo é o cheat-sheet rápido.

## Commands

```bash
./start.sh                                   # sobe o guardião (cria venv + deps + checa cadastro)

source .venv/bin/activate                    # ativa a venv p/ os comandos abaixo
python capture.py                            # 1x: tira fotos do dono (ESPACO/S=foto, Q/ESC=sai)
python enroll.py                             # 1x: gera encodings.npy a partir de known_faces/
python guardian.py                           # roda o guardião direto (sem o wrapper)

PYTHONPATH=. python -m pytest tests/ -v      # testes (precisa do PYTHONPATH — ver Gotchas)
```

Não há build nem lint configurados — é um app Python de script único por módulo.

## Architecture

- **Linguagem:** Python 3 (testado em 3.14, Homebrew/Apple Silicon).
- **Visão computacional:** `opencv-python` (captura) + `face_recognition`/dlib (embeddings de 128d).
- **GUI:** Tkinter (stdlib) — overlay fullscreen vermelho.
- **Concorrência:** detector roda em thread de fundo; overlay roda na main thread (exigência do Tkinter); comunicação por flag protegido com `Lock`.

Fluxo: `câmera → detector (known/unknown por quadro) → GuardianState (debounce) → flag → overlay (polling) → mostra/esconde`.

### Directory Structure

```
camera-guardian/
  config.py              # tunables (tolerance, debounce, downscale, liveness, textos)
  state.py               # GuardianState — máquina de estados pura (testada)
  liveness.py            # EAR + BlinkTracker — anti-spoofing por piscada (puro, testado)
  detector.py            # câmera + reconhecimento + liveness; read_counts() -> (known, unknown)
  capture.py             # ferramenta manual de fotos (webcam)
  enroll.py              # known_faces/* -> encodings.npy
  overlay.py             # alerta Tkinter fullscreen vermelho em TODOS os monitores
  guardian.py            # orquestra detector(thread) + state + overlay(main)
  start.sh               # launcher: venv + deps + check + guardian
  tests/test_state.py    # 8 testes da máquina de estados
  tests/test_liveness.py # 8 testes do EAR + BlinkTracker
  known_faces/         # fotos do dono (gitignored)
  encodings.npy        # cache de embeddings (gitignored, gerado por enroll.py)
  docs/superpowers/    # design + plano de implementação
```

## Comportamento (regra de produto)

Por quadro, prioridade: **DONO-VIVO > AMEAÇA > vazio (latch)**.
1. **Dono vivo presente** (reconhecido **e** piscou recentemente) → 🟩 limpa. Tem prioridade máxima: **não dispara nem com gente passando atrás**. O guardião protege quando o dono **sai**.
2. Senão, **ameaça** — rosto desconhecido **ou** o dono sem vivacidade (possível foto) → 🟥 alerta.
3. Quadro vazio → mantém o estado atual (continua vermelho até o dono vivo voltar).

Debounce: a troca de estado exige `DEBOUNCE_FRAMES` quadros consecutivos concordando (mata flicker).

**Liveness (anti-spoofing):** o dono só conta como "vivo" se piscou nos últimos `LIVENESS_WINDOW_FRAMES` quadros (EAR via landmarks dos olhos). Uma foto não pisca → nunca limpa. Custo: ~1-2s de vermelho quando o dono chega, até a primeira piscada.

## Key Patterns

- **Lógica pura isolada e testável** — `state.py` (decisão) e `liveness.py` (EAR + piscada) não dependem de câmera/GUI; toda a regra de negócio mora aí e é coberta por testes.
- **Liveness alimenta a máquina de estados** — o `detector` aplica reconhecimento + piscada e traduz cada quadro em `(dono_vivo, ameaça)`; o `state.py` só vê esses dois números (não muda quando a regra de liveness muda).
- **Threading detector(bg) / overlay(main)** — Tkinter só funciona na main thread; o detector publica o estado via `Lock`.
- **Overlay multi-monitor** — um `Toplevel` vermelho por tela (geometria via `screeninfo`), com fallback pra tela única.
- **Embeddings em `.npy`, não pickle** — `np.load`/`np.save` (sem execução de código arbitrário); fonte é local e confiável, mas `.npy` é o formato seguro e natural pra arrays (N,128).

## Gotchas

- **Nunca commitar `known_faces/` nem `encodings.npy`** — são dados biométricos do dono. Já estão no `.gitignore`. Ver [`docs/security.md`](./docs/security.md).
- **Testes precisam de `PYTHONPATH=.`** — não há `conftest.py`/pacote; `python -m pytest` a partir da raiz com `PYTHONPATH=.` resolve o `import state`.
- **Python 3.14 + `face_recognition`:** `face_recognition_models` usa `pkg_resources`, removido em `setuptools>=81`. Por isso `requirements.txt` fixa `setuptools<81`.
- **Tk ausente no Python Homebrew:** `import tkinter` falha (`_tkinter`) sem `brew install python-tk@<versão>`.
- **Foco de teclado no `capture.py`:** as teclas vão pro app em foco — é preciso **clicar na janela da câmera** antes de apertar ESPAÇO.
- **Permissão de câmera (macOS):** o terminal precisa de acesso em Ajustes do Sistema → Privacidade e Segurança → Câmera.

## Memory System

Memória persistente em `~/.claude/projects/-Users-gab-repo-camera-guardian/memory/` (não criada — projeto sem fatos não-óbvios a persistir). Checar `MEMORY.md` no início da sessão se existir.
