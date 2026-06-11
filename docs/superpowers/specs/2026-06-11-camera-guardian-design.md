# Camera Guardian — Design

**Data:** 2026-06-11
**Autor:** Gab
**Status:** Aprovado (aguardando revisão do spec)

## Objetivo

Um monitor de câmera para macOS que mantém o Mac fisicamente desbloqueado, mas
defendido. Quando um **rosto desconhecido** aparece na câmera, a tela inteira
fica **vermelha** com o texto gigante **"SAI DAI VAGABUNDO"**. Quando o **rosto
do dono (Gab)** reaparece, o alerta some. Brincadeira de escritório: zoar quem
mexe na máquina dos outros.

## Comportamento (regras de produto)

Por quadro da câmera, cada rosto detectado é classificado como **KNOWN** (Gab) ou
**UNKNOWN**. A decisão de alerta segue esta prioridade:

1. Existe pelo menos um rosto **UNKNOWN** → 🟥 **ALERTA** (desconhecido sempre
   ganha, mesmo se o Gab também estiver no quadro).
2. Senão, existe rosto **KNOWN** (Gab) → 🟩 **LIMPO**.
3. Quadro **sem rostos** → **mantém o estado atual** (se estava vermelho,
   continua vermelho até o Gab reaparecer).

Consequência da regra 3: depois que um intruso dispara o alerta, ele só é
liberado quando a cara do Gab é reconhecida — sair do quadro não basta.

### Debounce

Detecção de rosto pisca entre quadros. Para evitar troca de estado por um único
quadro ruim, a mudança de estado exige **N quadros consecutivos** concordando
(configurável). Isso vale para ligar e desligar o alerta.

## Arquitetura

Cinco módulos pequenos, cada um com uma responsabilidade única:

| Arquivo | Responsabilidade | Depende de |
|---|---|---|
| `enroll.py` | Captura/lê fotos do Gab → gera embeddings de 128d → grava `encodings.pkl` | face_recognition |
| `detector.py` | Loop de câmera; por quadro retorna contagem `{known, unknown}` | OpenCV, face_recognition |
| `state.py` | **Máquina de estados pura** (com debounce) — decide alerta on/off | nada |
| `overlay.py` | Janela Tkinter fullscreen vermelha; mostra/esconde | Tkinter |
| `guardian.py` | Orquestra: thread do detector → estado → overlay | os 4 acima |
| `config.py` | Tunables (tolerance, debounce N, downscale, modelo) | nada |

### Threading

Tkinter exige rodar na main thread.

- **Main thread:** roda o `overlay` (Tkinter `mainloop`).
- **Thread de fundo:** roda o `detector` (loop de câmera + reconhecimento) e
  alimenta o `state`, que expõe um flag `alert_active` thread-safe.
- O overlay faz polling via `root.after(100ms)` lendo o flag e
  mostra/esconde a janela vermelha.

### Fluxo de dados

```
câmera → detector (frame) → {known, unknown}
       → state.update(known, unknown) → alert_active (bool, debounced)
       → overlay polling → show/hide janela vermelha
```

## Reconhecimento

- Biblioteca `face_recognition` (dlib). Gera embedding de 128 dimensões por
  rosto.
- Enrollment: uma ou mais fotos do Gab em `known_faces/`, codificadas e
  cacheadas em `encodings.pkl`.
- Classificação: para cada rosto do quadro, compara a distância contra os
  encodings conhecidos; abaixo de `tolerance` (padrão 0.6) = KNOWN, senão
  UNKNOWN.
- Performance: quadro reduzido (downscale 1/4) antes da detecção; modelo HOG
  (CPU) para tempo real.

## Tratamento de erros

- **Câmera indisponível / sem permissão:** mensagem clara orientando liberar
  Câmera para o Terminal em Ajustes do Sistema → Privacidade e Segurança.
- **`encodings.pkl` ausente:** instrui rodar `enroll.py` primeiro.
- **Falha ao ler quadro:** pula o quadro e continua o loop.

## Testes

- `state.py`: **testes unitários puros (TDD)**. Alimenta sequências de
  classificações de quadro e verifica as transições do alerta, incluindo
  debounce, prioridade do UNKNOWN e a regra de "mantém estado em quadro vazio".
- `detector.py` / `overlay.py`: smoke test manual (dependem de câmera e tela).

## Estrutura de arquivos

```
camera-guardian/
  enroll.py
  detector.py
  state.py
  overlay.py
  guardian.py
  config.py
  known_faces/        # fotos de referência do Gab
  encodings.pkl       # cache (gerado por enroll.py)
  requirements.txt
  tests/
    test_state.py
  README.md
```

## Tunables (`config.py`)

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `TOLERANCE` | 0.6 | Distância máxima pra considerar KNOWN (menor = mais rígido) |
| `DEBOUNCE_FRAMES` | 3 | Quadros consecutivos pra trocar de estado |
| `DOWNSCALE` | 0.25 | Fator de redução do quadro antes da detecção |
| `DETECTION_MODEL` | "hog" | "hog" (CPU, rápido) ou "cnn" (GPU, preciso) |
| `ALERT_TEXT` | "SAI DAI VAGABUNDO" | Texto do alerta |
| `ALERT_BG` | vermelho | Cor de fundo do overlay |

## Fora de escopo (YAGNI)

- Som no alerta, múltiplos donos, logging/captura de fotos do intruso,
  empacotar como app `.app`. Podem entrar depois; não no MVP.
