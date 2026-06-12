# liveness.py — anti-spoofing por piscada. Lógica pura (sem câmera/GUI), testável.
import math
import config


def eye_aspect_ratio(eye):
    """EAR de um olho: 6 pontos (x, y) na ordem dos 68-landmarks.

    EAR = (|p1-p5| + |p2-p4|) / (2 * |p0-p3|). Alto = olho aberto, baixo = fechado.
    Retorna 0.0 se degenerado (largura horizontal nula).
    """
    def dist(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    vert = dist(eye[1], eye[5]) + dist(eye[2], eye[4])
    horiz = dist(eye[0], eye[3])
    return vert / (2.0 * horiz) if horiz else 0.0


class BlinkTracker:
    """Diz se o dono está 'vivo' (piscou recentemente) a partir do EAR por quadro.

    `update(ear)` a cada quadro — `ear` é o EAR médio do dono, ou None se o dono
    não está visível. Uma transição fechado→aberto conta como piscada. A
    vivacidade expira após `window_frames` quadros sem nova piscada e ZERA após
    o dono ausente por `reset_absent_frames` quadros (impede que uma foto
    'herde' a vivacidade que o dono real deixou para trás).
    """

    def __init__(self, ear_threshold=config.EAR_THRESHOLD,
                 consec_frames=config.BLINK_CONSEC_FRAMES,
                 window_frames=config.LIVENESS_WINDOW_FRAMES,
                 reset_absent_frames=config.LIVENESS_RESET_ABSENT):
        self.ear_threshold = ear_threshold
        self.consec_frames = consec_frames
        self.window_frames = window_frames
        self.reset_absent_frames = reset_absent_frames
        self._closed_streak = 0
        self._absent_streak = 0
        self._since_blink = None  # None = nunca piscou (ou foi resetado)

    def update(self, ear):
        if ear is None:
            self._absent_streak += 1
            self._closed_streak = 0
            if self._absent_streak >= self.reset_absent_frames:
                self._since_blink = None
        else:
            self._absent_streak = 0
            if ear < self.ear_threshold:
                self._closed_streak += 1
            else:
                if self._closed_streak >= self.consec_frames:
                    self._since_blink = 0  # acabou de piscar (fechado→aberto)
                self._closed_streak = 0
        if self._since_blink is not None:
            self._since_blink += 1
        return self.is_live()

    def is_live(self):
        return self._since_blink is not None and self._since_blink <= self.window_frames
