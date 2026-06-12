# Claude Code — Hints Locais (Camera Guardian)

> **Docs canônicos um nível acima.** Leia `../CLAUDE.md` primeiro, depois `../AGENTS.md`. Este arquivo só adiciona guardrails específicos do Claude Code.

## Tools

Use as tools nativas do Claude Code — **não** nomes estilo Copilot/Cursor:

| Ação | Tool |
|---|---|
| Ler arquivo | `Read` (path absoluto) |
| Editar no lugar | `Edit` (precisa `Read` antes) |
| Criar/sobrescrever | `Write` |
| Buscar arquivos | `Glob` |
| Buscar conteúdo | `Grep` |
| Shell | `Bash` |

Working directory: `/Users/gab/repo/camera-guardian`.

## Never Modify / Never Commit

- `.git/`, `.venv/` — controle de versão / ambiente
- **`known_faces/` e `encodings.npy`** — dados biométricos do dono; já no `.gitignore`. **Nunca** force-add nem remova do ignore.
- `.claude/` — config do harness

## Session Workflow

1. **Antes de mexer em `state.py`** — rode os testes pra ter baseline: `PYTHONPATH=. python -m pytest tests/ -v`.
2. **Mantenha `state.py` puro** — sem import de `cv2`/`tkinter`/`numpy`. Lógica de I/O vai nos outros módulos.
3. **Tkinter só na main thread** — não mexa em widgets a partir da thread do detector.
4. **Antes de declarar pronto** — testes verdes + smoke manual do caminho de câmera/GUI quando aplicável (ver `../AGENTS.md` §4-5).

## Testing Shortcuts

```bash
source .venv/bin/activate
PYTHONPATH=. python -m pytest tests/ -v                                   # todos
PYTHONPATH=. python -m pytest tests/test_state.py::test_comeca_limpo -v   # um teste
```

> O hook RTK pode reescrever `pytest`; se vier "No tests collected", rode com `rtk proxy python -m pytest ...` ou direto pelo binário da venv.

## Memory

Memória persistente em `~/.claude/projects/-Users-gab-repo-camera-guardian/memory/` (pode não existir). Não duplique o que já está em `CLAUDE.md`/`AGENTS.md`/`git log`/código — memória é pra *surpresas* e *preferências*.
