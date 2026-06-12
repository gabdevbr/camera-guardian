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
    print("Clique NA JANELA da câmera primeiro. ESPAÇO/S = foto | Q/ESC = sair")
    window = "Capture - clique aqui, ESPACO=foto, Q=sair"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            continue
        # `frame` fica LIMPO p/ salvar; o texto vai só na cópia de exibição.
        display = frame.copy()
        cv2.putText(display, "Clique aqui e aperte ESPACO p/ foto (Q=sair)",
                    (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display, f"Fotos salvas: {n}",
                    (12, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow(window, display)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord(" "), ord("s")):
            path = os.path.join(config.KNOWN_FACES_DIR, f"gab_{n:02d}.jpg")
            cv2.imwrite(path, frame)  # salva o frame limpo, sem o texto
            print(f"[salvo] {path}")
            n += 1
        elif key in (ord("q"), 27):  # 27 = ESC
            break
    cap.release()
    cv2.destroyAllWindows()
    print(f"{n} foto(s) salvas em {config.KNOWN_FACES_DIR}/")


if __name__ == "__main__":
    main()
