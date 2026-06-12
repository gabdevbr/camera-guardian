# guardian.py — detector(thread de fundo) → state → overlay(main thread).
import threading
import config
from detector import Detector
from state import GuardianState
from overlay import Overlay
from liveness import BlinkTracker


def main():
    blink = BlinkTracker(
        ear_threshold=config.EAR_THRESHOLD,
        consec_frames=config.BLINK_CONSEC_FRAMES,
        window_frames=config.LIVENESS_WINDOW_FRAMES,
        reset_absent_frames=config.LIVENESS_RESET_ABSENT,
    )
    detector = Detector(
        config.ENCODINGS_PATH,
        config.CAMERA_INDEX,
        config.DOWNSCALE,
        config.DETECTION_MODEL,
        config.TOLERANCE,
        blink_tracker=blink,
    )
    state = GuardianState(debounce_frames=config.DEBOUNCE_FRAMES)
    stop = threading.Event()
    lock = threading.Lock()
    alert = {"value": False}

    def loop():
        while not stop.is_set():
            counts = detector.read_counts()
            if counts is None:
                continue
            known, unknown = counts
            active = state.update(known, unknown)
            with lock:
                alert["value"] = active

    worker = threading.Thread(target=loop, daemon=True)
    worker.start()

    def get_alert():
        with lock:
            return alert["value"]

    overlay = Overlay(get_alert, config.POLL_MS)
    try:
        overlay.run()
    finally:
        stop.set()
        detector.release()


if __name__ == "__main__":
    main()
