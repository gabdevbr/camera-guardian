# enroll.py — lê known_faces/* → embeddings de 128d → encodings.npy
import glob
import os
import face_recognition
import numpy as np
import config


def build_encodings(faces_dir, out_path):
    patterns = ("*.jpg", "*.jpeg", "*.png")
    paths = sorted(
        p for pat in patterns for p in glob.glob(os.path.join(faces_dir, pat))
    )
    if not paths:
        raise SystemExit(
            f"Sem fotos em {faces_dir}/. Rode `python capture.py` primeiro "
            f"ou coloque fotos suas (jpg/png) na pasta."
        )
    encodings = []
    for p in paths:
        img = face_recognition.load_image_file(p)
        encs = face_recognition.face_encodings(img)
        if not encs:
            print(f"[pula] nenhum rosto em {p}")
            continue
        encodings.append(encs[0])
        print(f"[ok] {p}")
    if not encodings:
        raise SystemExit("Nenhum rosto detectado nas fotos.")
    # Array (N, 128) salvo como .npy — formato seguro, sem pickle.
    np.save(out_path, np.array(encodings))
    print(f"Salvo {len(encodings)} encoding(s) em {out_path}")


if __name__ == "__main__":
    build_encodings(config.KNOWN_FACES_DIR, config.ENCODINGS_PATH)
