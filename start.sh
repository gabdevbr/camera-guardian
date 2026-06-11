#!/usr/bin/env bash
# start.sh — sobe o Camera Guardian dentro da venv, cuidando do setup na primeira vez.
set -euo pipefail

# Sempre opera a partir da pasta do script (funciona de qualquer lugar).
cd "$(dirname "$0")"

VENV=".venv"
PY="$VENV/bin/python"

# 1) venv
if [[ ! -d "$VENV" ]]; then
  echo "==> Criando ambiente virtual (.venv)..."
  python3 -m venv "$VENV"
fi

# 2) dependências (instala só se faltar algo)
if ! "$PY" -c "import cv2, face_recognition, numpy, tkinter" >/dev/null 2>&1; then
  echo "==> Instalando dependências (dlib compila, pode demorar alguns minutos)..."
  "$PY" -m pip install -q -U pip
  "$PY" -m pip install -q -r requirements.txt
  # _tkinter é módulo do sistema; avisa se o Python não tiver Tk.
  if ! "$PY" -c "import tkinter" >/dev/null 2>&1; then
    echo "!! Falta o Tk no seu Python. Instale com: brew install python-tk@\$(\"$PY\" -c 'import sys;print(f\"{sys.version_info.major}.{sys.version_info.minor}\")')"
    exit 1
  fi
fi

# 3) precisa do rosto cadastrado
ENCODINGS="$("$PY" -c "import config; print(config.ENCODINGS_PATH)")"
if [[ ! -f "$ENCODINGS" ]]; then
  echo "!! Você ainda não cadastrou seu rosto ($ENCODINGS não existe)."
  echo "   Rode primeiro:"
  echo "     $PY capture.py    # tira fotos (ESPACO=foto, Q=sai)"
  echo "     $PY enroll.py     # gera $ENCODINGS"
  exit 1
fi

# 4) sobe o guardião
echo "==> Iniciando Camera Guardian. ESC esconde o alerta, Ctrl+C encerra."
exec "$PY" guardian.py
