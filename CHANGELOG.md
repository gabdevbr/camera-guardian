# Changelog

Mudanças notáveis do **Camera Guardian**. Formato baseado em [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

> **Fonte da verdade:** `git log`. Este arquivo é um resumo humano — se divergir do git, o git vence. Regenerar com:
>
> ```bash
> git log --oneline --no-merges
> ```

---

## [Unreleased]

### Conhecido / em aberto
- **Spoofing por foto.** Mostrar uma foto do dono (impressa ou na tela do celular) burla o reconhecimento — a v1 não tem detecção de vivacidade (*liveness*). Ver [`docs/security.md`](./docs/security.md) e [`docs/troubleshooting.md`](./docs/troubleshooting.md). Anti-spoofing planejado.

---

## 2026-06-12 — MVP funcional

### Added
- **Máquina de estados `GuardianState`** com debounce e regra UNKNOWN > KNOWN > latch; 8 testes unitários. (`6e2cf3e`)
- **Pipeline de reconhecimento** — `detector.py` (OpenCV + face_recognition), `capture.py` (fotos do dono pela webcam), `enroll.py` (embeddings → `encodings.npy`). (`6e2cf3e`)
- **Overlay** Tkinter fullscreen vermelho com show/hide por polling. (`6e2cf3e`)
- **Orquestração** `guardian.py` — detector em thread de fundo + overlay na main thread. (`6e2cf3e`)
- **`start.sh`** — launcher que cria a venv, instala deps e valida o cadastro antes de subir. (`c754575`)
- **Licença MIT** + repo open source. (`bdbe54e`)

### Changed
- **Embeddings em `.npy` (numpy) em vez de pickle** — formato seguro, sem execução de código arbitrário. (`6e2cf3e`)
- **`capture.py`** ganhou instruções na própria janela, contador de fotos e aceita `S`/`ESC`; salva o frame limpo (sem o texto sobreposto). (`24a1992`)

### Fixed
- **`face_recognition_models` no Python 3.14** — `pkg_resources` foi removido em `setuptools>=81`; fixado `setuptools<81` no `requirements.txt`. (`6e2cf3e`)

---

## Política de changelog

- **Commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`).
- **Mudança visível ao usuário** entra num único commit com docs/config relacionados.
- **Breaking changes** prefixam `BREAKING:` no corpo do commit e listam nota de migração aqui antes do release.
