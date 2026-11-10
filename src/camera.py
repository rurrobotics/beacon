import cv2
import time
import threading
import numpy as np
from flask import Flask, Response

app = Flask(__name__)
_latest = None                  # najnoviji frejm
_lock = threading.Lock()

# 4 ID u uglovima
PIXEL_POINTS = np.float32()
TABLE_POINTS = np.float32()
H = cv2.getPerspectiveTransform(PIXEL_POINTS, TABLE_POINTS)

def pixel_to_mm(px, py):
    p = cv2.perspectiveTransform(np.float32([[[px, py]]]), H)[0][0]
    return int(p[0]), int(p[1])

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
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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
    # vrti se zauvek u mainu
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
                for c, i in zip(corners, ids.flatten()):
                    cx, cy = c[0].mean(axis=0)  # koordinate u odnosu na centar id polja
                    x, y = pixel_to_mm(cx, cy)
                    found.append((int(i), x, y))

            if detected is not None:
                detected(found)

            ok, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ok:
                with _lock:
                    _latest = jpg.tobytes()

    finally:
        cap.release()
