import cv2
import time
import threading
import numpy as np
from flask import Flask, Response

app = Flask(__name__)
_latest = None                  # najnoviji frejm
_lock = threading.Lock()

# 4 ID u uglovima (20, 21, 22, 23)
# koordinatni pocetak u gornjem levom uglu
CORNER_TAGS_MM = {
    20: (600, 600),
    21: (2400, 600),
    22: (600, 1400),
    23: (2400, 1400)
}

TABLE_WIDTH_MM = 3000
TABLE_HEIGHT_MM = 2000
SCALE = 0.3
OUT_SIZE = (int(TABLE_WIDTH_MM * SCALE), int(TABLE_HEIGHT_MM * SCALE))
S = np.diag([SCALE, SCALE, 1.0])
SMOOTH = 0.2
H = None

def pixel_to_mm(px, py):
    if H is None:
        return None
    p = cv2.perspectiveTransform(np.float32([[[px, py]]]), H)[0][0]
    return int(p[0]), int(p[1])

def update_homography(centers):
    global H
    seen = [i for i in CORNER_TAGS_MM if i in centers]
    if len(seen) < 4:
        H = None    # obrisi ovo posle, vraca warpovanje u normalu a ne treba to da radi
        return
    pixels = np.float32([centers[i] for i in seen])
    table = np.float32([CORNER_TAGS_MM[i] for i in seen])
    H1, _ = cv2.findHomography(pixels, table)
    if H1 is None:
        return
    
    H1 /= H1[2, 2]
    H = H1 if H is None else (1 - SMOOTH) * H + SMOOTH * H1

# vraca funkciju koja vraca koordinate uglova id-ja i koji je id u pitanju
def id_detection():
    aruco = cv2.aruco
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)

    if hasattr(aruco, "ArucoDetector"):
        detector = aruco.ArucoDetector(dictionary, aruco.DetectorParameters())
        return lambda gray: detector.detectMarkers(gray)[:2]
    params = aruco.DetectorParameters_create()
    return lambda gray: aruco.detectMarkers(gray, dictionary, parameters=params)[:2]

def open_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        raise SystemExit("Camera didn't open")

    return cap

# kod za streamovanje kamere u browseru na linku http://192.168.137.45:8000
@app.route("/")
def stream():
    def gen():
        while True:
            with _lock:
                jpg = _latest
            if jpg is not None:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
            time.sleep(0.03)
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

def run(detected=None):
    # vrti se zauvek
    global _latest

    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=8000, threaded=True, use_reloader=False), daemon=True, name="web"
    ).start()

    detect = id_detection()
    cap = open_camera()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("No frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids = detect(gray)

            found = []
            if ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)

                centers = {}
                for c, i in zip(corners, ids.flatten()):        # zip uparuje clanove dva niza
                    centers[int(i)] = c[0].mean(axis=0)         # centri svih id-jeva na tabli

                update_homography(centers)
                print({i: tuple(int(v) for v in centers[i]) for i in CORNER_TAGS_MM if i in centers})

                for i, (cx, cy) in centers.items():
                    if i in CORNER_TAGS_MM:
                        continue
                    pos = pixel_to_mm(cx, cy)
                    if pos is not None:
                        found.append((i, pos[0], pos[1]))

            if detected is not None:
                detected(found)

            # warpovana slika kao iz pticije
            if H is not None:
                view = cv2.warpPerspective(frame, S @ H, OUT_SIZE)
                for i, x, y in found:
                    p = (int(x * SCALE), int(y * SCALE))
                    # crtanje gde su tagovi
                    cv2.circle(view, p, 5, (0, 0, 255), -1)
                    cv2.putText(view, f"{i}:{x},{y}", (p[0] + 6, p[1] - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            else:
                view = frame

            ok, jpg = cv2.imencode(".jpg", view, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ok:
                with _lock:
                    _latest = jpg.tobytes()

    finally:
        cap.release()

def stop():
    _stop.set()