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

## ⚠️ Limitação conhecida: spoofing por foto (sem liveness)

A v1 **não detecta vivacidade** (*liveness*). O reconhecimento compara embeddings — uma **foto do dono** (impressa ou na tela de um celular) gera um embedding parecido o suficiente e **burla o guardião**: ele trata a foto como o dono e não dispara.

**Impacto:** qualquer pessoa com uma foto sua consegue desarmar o alerta.

**Mitigação na v1:** nenhuma efetiva. Reduzir `TOLERANCE` (ex.: `0.5`) torna o match mais rígido e às vezes atrapalha fotos de baixa qualidade, mas **não** resolve — uma foto boa ainda passa.

**Hardening planejado (anti-spoofing / liveness):**
- **Detecção de piscada / micro-movimento** entre quadros (foto estática não pisca).
- **Análise de textura / moiré** pra distinguir pele de tela de celular (LBP, frequência).
- **Challenge-response** (ex.: "vire a cabeça") quando há dúvida.
- **Profundidade** se houver câmera com sensor de depth.

Enquanto não houver liveness, trate o guardião como **dissuasão/brincadeira**, não controle de acesso real.

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
