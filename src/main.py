import threading
import time

import comms
import camera

stop = threading.Event()

def main():
    t_cam = threading.Thread(target=camera.run, args=(stop,), name="camera")
    t_com = threading.Thread(target=comms.run, args=(stop,), name="comms")

    t_cam.start()
    t_com.start()

    try:
        while t_cam.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        t_cam.join()
        t_com.join()

if __name__ == "__main__":
    main()