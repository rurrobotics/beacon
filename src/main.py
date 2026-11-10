import time

import comms
import camera

comms.start_sender()

try:
    #camera.run(detected=comms.set_simas)                   # kada se uspostavi kamera
    comms.set_simas([(1, 500, 800), (2, 2100, 300), (3, 210, 305), (4, 100, 1300), (5, 2000, 300)])        # random
except KeyboardInterrupt:
    pass
finally:
    comms.stop_sender()
    #cam.release()