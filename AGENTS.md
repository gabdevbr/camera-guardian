# AGENTS.md — Regras de Engenharia (Camera Guardian)

Diretrizes para agentes de IA e contribuidores neste repositório. **Camera Guardian** é um monitor de câmera para macOS que dispara um overlay vermelho fullscreen ("SAI DAI VAGABUNDO") quando um rosto desconhecido aparece e o limpa quando o dono reaparece. App desktop Python pequeno, single-purpose. Leia [`CLAUDE.md`](./CLAUDE.md) primeiro (cheat-sheet); este arquivo aprofunda.

---

## 1. Mindset

- Solução mais simples que resolve vence (KISS, YAGNI). Este projeto cabe num punhado de módulos focados — mantenha assim.
- Antecipe falhas de hardware: câmera ausente, sem permissão, quadro corrompido, sem rosto. Cada caminho tem tratamento explícito — não regrida isso.
- **Nome revela intenção.** `read_counts`, `GuardianState`, `alert_active` — siga o padrão.
- Sem valores mágicos: tudo que é ajustável mora em [`config.py`](./config.py).

---

## 2. Arquitetura

| Camada | Arquivo | Responsabilidade | Depende de |
|---|---|---|---|
| Config | `config.py` | Tunables | — |
| Decisão | `state.py` | Máquina de estados pura | — (testável) |
| Percepção | `detector.py` | Câmera + reconhecimento → `(known, unknown)` | OpenCV, face_recognition |
| Cadastro | `capture.py`, `enroll.py` | Fotos do dono → `encodings.npy` | OpenCV / face_recognition, numpy |
| Apresentação | `overlay.py` | Janela Tkinter vermelha | Tkinter |
| Orquestração | `guardian.py` | Cola tudo (thread + main) | os acima |

**Invariantes:**
- `state.py` **não importa** OpenCV, Tkinter ou numpy. Lógica pura, sem I/O. É a fronteira testável — não a contamine.
- Tkinter roda **só na main thread**. O detector roda em thread de fundo e publica o estado por trás de um `Lock`. Nunca toque em widgets Tk fora da main thread.
- Embeddings persistem em `.npy` (numpy), **nunca pickle**.

---

## 3. Comportamento (contrato da máquina de estados)

Prioridade por quadro: **UNKNOWN > KNOWN > vazio (latch no estado atual)**. Debounce de `DEBOUNCE_FRAMES` quadros consecutivos pra trocar. Qualquer mudança em `state.py` **precisa** manter os 8 testes verdes e adicionar testes pros novos casos.

---

## 4. Testes

- **Regra:** toda lógica tem teste. A lógica de decisão está isolada em `state.py` justamente pra ser 100% testável sem hardware.
- **Cobertura mínima:** `state.py` em 100% de branches. Câmera/GUI (`detector`, `overlay`, `capture`) são smoke-test manual (dependem de webcam/tela) — documentar o passo manual no PR.
- **Rodar:**
  ```bash
  PYTHONPATH=. python -m pytest tests/ -v
  ```

---

## 5. Checklist de auto-revisão (antes de entregar)

- [ ] `state.py` continua puro (sem import de cv2/tkinter/numpy)?
- [ ] Nenhum acesso a widget Tk fora da main thread?
- [ ] Novos tunables foram pra `config.py` (sem hardcode)?
- [ ] Edge cases de hardware tratados (sem câmera, sem permissão, quadro `None`, sem rosto)?
- [ ] `PYTHONPATH=. python -m pytest tests/ -v` passa?
- [ ] Novos comportamentos da máquina de estados têm teste?
- [ ] Nenhum dado biométrico (`known_faces/`, `encodings.npy`) entrou no commit?
- [ ] Commit em Conventional Commits?

---

## 6. Convenções

| Contexto | Convenção |
|---|---|
| Funções/variáveis | `snake_case` |
| Classes | `PascalCase` (`GuardianState`, `Detector`, `Overlay`) |
| Constantes | `SCREAMING_SNAKE_CASE` (em `config.py`) |
| Arquivos de teste | `tests/test_*.py` |
| Commits | Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`) |

Imports: stdlib → terceiros → `config`/locais. Documentação e comentários em português (idioma dominante do projeto).

---

## 7. Segurança & privacidade

Este app processa **biometria** (rostos) e mantém a câmera aberta. Regras invioláveis em [`docs/security.md`](./docs/security.md): nada de dados biométricos no git; processamento 100% local; nenhuma imagem ou embedding sai da máquina.

---

*Este documento é a autoridade sobre como operar neste repositório. Desvios devem ser justificados tecnicamente.*
