# config.py — tunables do Camera Guardian

TOLERANCE = 0.6          # distância máx. p/ considerar KNOWN (menor = mais rígido)
DEBOUNCE_FRAMES = 3      # quadros consecutivos p/ trocar de estado
DOWNSCALE = 0.25         # fator de redução do quadro antes da detecção
DETECTION_MODEL = "hog"  # "hog" (CPU, rápido) ou "cnn" (GPU, preciso)

CAMERA_INDEX = 0
POLL_MS = 100            # intervalo de polling do overlay (ms)

ENCODINGS_PATH = "encodings.npy"
KNOWN_FACES_DIR = "known_faces"

ALERT_TEXT = "SAI DAI VAGABUNDO"
ALERT_BG = "#cc0000"     # vermelho
ALERT_FG = "#ffffff"     # texto branco
ALERT_FONT_SIZE = 120
