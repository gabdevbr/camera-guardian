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

## Uso

Cadastro do rosto (uma vez):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python capture.py    # tira fotos (ESPACO=foto, Q=sai)
python enroll.py     # gera encodings.npy
```

Ligar o guardião — o `start.sh` cuida da venv, das dependências e do
check de cadastro automaticamente:

```bash
./start.sh
```

ESC esconde o alerta na hora; Ctrl+C encerra.

Requer permissão de **Câmera** para o terminal em
Ajustes do Sistema → Privacidade e Segurança.

> ⚠️ **Limitação conhecida:** a v1 não detecta vivacidade — mostrar uma **foto** do dono (no celular ou impressa) burla o reconhecimento. É dissuasão/brincadeira, não controle de acesso. Anti-spoofing no roadmap — ver [`docs/security.md`](docs/security.md).

## Documentação

| Doc | Para quê |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Cheat-sheet: comandos, arquitetura, gotchas |
| [`AGENTS.md`](AGENTS.md) | Regras de engenharia e convenções |
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de mudanças |
| [`docs/security.md`](docs/security.md) | Privacidade, biometria, spoofing |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Erros comuns + correções |
| [`docs/superpowers/`](docs/superpowers/) | Design e plano de implementação |

## Licença

[MIT](LICENSE) © gabdevbr
