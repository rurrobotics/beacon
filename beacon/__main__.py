import time

from . import camera, comms


def main():
    comms.start_sender()

    try:
        while True:
            camera.run(detected=comms.set_simas)                   # kada se uspostavi kamera
            #comms.set_simas([(i, random.randint(0, 3000), random.randint(0, 2000))
                             #for i in range(1, 6)])        # random
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        comms.stop_sender()


if __name__ == "__main__":
    main()
