import cv2
import time
import threading
from flask import Flask, Response

app = Flask(__name__)
_latest = None                  # najnoviji frejm
_lock = threading.Lock()

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

def run(stop, ids_q=None):
    global _latest

    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=8000, threaded=True, use_reloader=False), daemon=True, name="web"
    ).start()

    detect = id_detection()
    cap = open_camera()

    try:
        while not stop.is_set():
            ok, frame = cap.read()
            if not ok:
                print("No frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids = detect(gray)

            if ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                found = ids.flatten().tolist()
                print("IDs:", found)
                if ids_q is not None:
                    try:
                        ids_q.put_nowait((time.time(), found))
                    except Exception:
                        pass 

            ok, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ok:
                with _lock:
                    _latest = jpg.tobytes()

    finally:
        cap.release()
