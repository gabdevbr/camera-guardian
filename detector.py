# detector.py — câmera + reconhecimento + liveness; mapeia cada quadro p/ a máquina de estados.
import cv2
import face_recognition
import numpy as np
from liveness import BlinkTracker, eye_aspect_ratio


class Detector:
    def __init__(self, encodings_path, camera_index, downscale, model, tolerance,
                 blink_tracker=None):
        try:
            # allow_pickle=False (padrão): só lê o array (N,128), sem código arbitrário.
            self.known = np.load(encodings_path)
        except FileNotFoundError:
            raise SystemExit(
                f"Sem {encodings_path}. Rode `python enroll.py` primeiro."
            )
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise SystemExit(
                "Não consegui abrir a câmera. Libere Câmera pro Terminal em "
                "Ajustes do Sistema → Privacidade e Segurança → Câmera."
            )
        self.downscale = downscale
        self.model = model
        self.tolerance = tolerance
        self.blink = blink_tracker or BlinkTracker()

    def _owner_ear(self, frame, small_location):
        """EAR médio do dono, medido em resolução cheia p/ precisão. None se sem olhos."""
        inv = 1.0 / self.downscale
        top, right, bottom, left = small_location
        full_loc = (int(top * inv), int(right * inv), int(bottom * inv), int(left * inv))
        rgb_full = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        landmarks = face_recognition.face_landmarks(rgb_full, [full_loc])
        if not landmarks:
            return None
        lm = landmarks[0]
        if "left_eye" not in lm or "right_eye" not in lm:
            return None
        return (eye_aspect_ratio(lm["left_eye"]) + eye_aspect_ratio(lm["right_eye"])) / 2.0

    def read_counts(self):
        """Retorna (known, unknown) p/ a máquina de estados, ou None se a leitura falhar.

        known   = 1 se o DONO VIVO está presente (piscou recentemente), senão 0.
        unknown = 1 se há AMEAÇA — rosto desconhecido OU o dono sem vivacidade
                  (possível foto) — senão 0.
        """
        ok, frame = self.cap.read()
        if not ok:
            return None
        small = cv2.resize(frame, (0, 0), fx=self.downscale, fy=self.downscale)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model=self.model)
        encodings = face_recognition.face_encodings(rgb, locations)

        unknown = 0
        owner_idx = owner_dist = None
        for i, enc in enumerate(encodings):
            distances = face_recognition.face_distance(self.known, enc)
            d = float(distances.min()) if len(distances) else 1.0
            if d <= self.tolerance:
                if owner_dist is None or d < owner_dist:  # melhor match = o dono
                    owner_idx, owner_dist = i, d
            else:
                unknown += 1

        owner_present = owner_idx is not None
        owner_ear = self._owner_ear(frame, locations[owner_idx]) if owner_present else None
        owner_live = self.blink.update(owner_ear)  # chamado SEMPRE (rastreia ausência)

        live_owner = owner_present and owner_live
        threat = (unknown > 0) or (owner_present and not owner_live)
        return (1 if live_owner else 0, 1 if threat else 0)

    def release(self):
        self.cap.release()
