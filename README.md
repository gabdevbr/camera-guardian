# Camera Guardian 🟥

Monitor de câmera para macOS que mantém o Mac desbloqueado, mas defendido.
Quando um **rosto desconhecido** aparece na câmera, a tela inteira fica
**vermelha** com o texto gigante **"SAI DAI VAGABUNDO"**. Quando a cara do dono
reaparece, o alerta some.

> Status: em desenvolvimento. Veja o design em
> [`docs/superpowers/specs/`](docs/superpowers/specs/).

## Como funciona

Por quadro da câmera, cada rosto é classificado como **conhecido** (você) ou
**desconhecido**:

1. Rosto desconhecido → 🟥 alerta vermelho
2. Sua cara → 🟩 limpa
3. Quadro vazio → mantém o estado (continua vermelho até você voltar)

Reconhecimento de identidade via [`face_recognition`](https://github.com/ageitgey/face_recognition)
(embeddings de 128 dimensões); overlay fullscreen via Tkinter.

## Setup (em breve)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python enroll.py     # cadastra seu rosto
python guardian.py   # liga o guardião
```

Requer permissão de **Câmera** para o Terminal em
Ajustes do Sistema → Privacidade e Segurança.
