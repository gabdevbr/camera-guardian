# Security & Privacidade

O Camera Guardian processa **dados biométricos** (rostos) e mantém a **câmera aberta** continuamente. Este doc define o modelo de privacidade e as limitações de segurança conhecidas.

---

## Princípio: tudo local

- **Nenhum dado sai da máquina.** Captura, embeddings e reconhecimento rodam 100% local (OpenCV + dlib). Não há rede, telemetria, nuvem ou API externa.
- **Nada de biometria no git.** `known_faces/` (fotos do dono) e `encodings.npy` (embeddings de 128d) estão no [`.gitignore`](../.gitignore). Nunca commitar.
- **Sem áudio, sem gravação.** O app não grava vídeo nem salva quadros da operação — só lê o quadro atual, decide, e descarta.

### O que é armazenado

| Artefato | Conteúdo | Local | Versionado? |
|---|---|---|---|
| `known_faces/*.jpg` | Fotos do dono (cadastro) | Disco local | ❌ gitignored |
| `encodings.npy` | Embeddings de 128d do dono | Disco local | ❌ gitignored |
| (em memória) | Quadro atual da câmera | RAM, efêmero | ❌ nunca persistido |

---

## Superfície de ataque

```
[câmera física] → [detector local] → [decisão] → [overlay]
       ▲
       └── único vetor de entrada: o que aparece na frente da lente
```

Não há porta de rede, endpoint nem entrada de usuário remota. O único vetor é **o que é apresentado à câmera**.

---

## Anti-spoofing: liveness por piscada

O reconhecimento sozinho compara só *aparência* — uma **foto do dono** (impressa ou na tela do celular) gera um embedding parecido e burlaria o guardião. Por isso o dono só conta como presente se estiver **vivo**.

**Mitigação ativa (implementada):** detecção de piscada via **EAR** (Eye Aspect Ratio) sobre os landmarks dos olhos (`liveness.py`). O dono só "limpa" o alerta se piscou dentro de `LIVENESS_WINDOW_FRAMES` quadros. Uma foto estática **não pisca** → nunca é tratada como o dono vivo → não desarma o alerta. A vivacidade ainda **zera** quando o dono some por alguns quadros (`LIVENESS_RESET_ABSENT`), pra uma foto não "herdar" a piscada que o dono real deixou.

**Custo de UX:** quando o dono chega, há ~1-2s de vermelho até a primeira piscada (todo mundo pisca involuntariamente em segundos).

### Risco residual (não coberto)

- **Replay de vídeo do dono** — um vídeo (no celular) onde o dono pisca pode passar pela detecção de piscada. Defesas mais fortes (textura/moiré anti-tela, challenge-response, profundidade) ficam pro futuro.
- Tratar o guardião como **dissuasão forte**, não controle de acesso de nível bancário.

### Hardening futuro

- Análise de textura / moiré pra distinguir pele de tela de celular (LBP, frequência).
- Challenge-response ("vire a cabeça") quando há dúvida.
- Profundidade, se houver câmera com sensor de depth.

---

## Permissões

- **Câmera (macOS):** o terminal/app precisa de permissão em Ajustes do Sistema → Privacidade e Segurança → Câmera. Sem isso, `capture.py`/`guardian.py` falham com erro claro.
- O app **não** pede rede, disco fora da pasta do projeto, nem outros recursos.

---

## Nunca commitar

- `known_faces/` (fotos reais)
- `encodings.npy` (embeddings)
- Qualquer screenshot/gravação contendo rostos

## Checklist de segurança para nova feature

- [ ] Nenhuma biometria nova vaza pro git (atualizar `.gitignore` se criar novos artefatos)
- [ ] Processamento continua 100% local (sem rede/telemetria)
- [ ] Quadros da câmera continuam efêmeros (não persistir sem motivo explícito)
- [ ] Se tocar reconhecimento, considerar o vetor de spoofing acima
