# detector.py — lê a câmera e classifica rostos como known/unknown por quadro.
import cv2
import face_recognition
import numpy as np


class Detector:
    def __init__(self, encodings_path, camera_index, downscale, model, tolerance):
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

    def read_counts(self):
        """Retorna (known, unknown) do quadro atual, ou None se a leitura falhar."""
        ok, frame = self.cap.read()
        if not ok:
            return None
        small = cv2.resize(frame, (0, 0), fx=self.downscale, fy=self.downscale)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model=self.model)
        encodings = face_recognition.face_encodings(rgb, locations)
        known = unknown = 0
        for enc in encodings:
            distances = face_recognition.face_distance(self.known, enc)
            if len(distances) and distances.min() <= self.tolerance:
                known += 1
            else:
                unknown += 1
        return known, unknown

    def release(self):
        self.cap.release()
