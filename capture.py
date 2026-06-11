# capture.py — tira fotos da webcam p/ enrollment. ESPAÇO=foto, Q=sair.
import os
import cv2
import config


def main():
    os.makedirs(config.KNOWN_FACES_DIR, exist_ok=True)
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        raise SystemExit(
            "Não consegui abrir a câmera. Libere Câmera pro Terminal em "
            "Ajustes do Sistema → Privacidade e Segurança → Câmera."
        )
    print("ESPAÇO = tirar foto | Q = sair")
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            continue
        cv2.imshow("Capture (ESPACO=foto, Q=sair)", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(" "):
            path = os.path.join(config.KNOWN_FACES_DIR, f"gab_{n:02d}.jpg")
            cv2.imwrite(path, frame)
            print(f"[salvo] {path}")
            n += 1
        elif key == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
    print(f"{n} foto(s) salvas em {config.KNOWN_FACES_DIR}/")


if __name__ == "__main__":
    main()
