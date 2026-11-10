import socket
import time
import struct
import threading

# slanje paketa koordinata sima
# 1. HDR - tip, verzija, rb paketa, br sima
# 2. ENT - id, x_mm, y_mm

# imena varijabli koje pocinju sa _ su interne u fajlu

PICOS = [("192.168.137.17", 5005)] # bice ih jos u buducnosti
RATE = 5                # 5Hz, 5 paketa u sekundi
MAX_SIMA = 6

HDR = "<BBIB"
ENT = "<Bhh"

_latest = []                # kamera detektuje sve vreme, paket se salje na svakih 200ms, treba da posalje poslednje
_lock = threading.Lock()
_stop = threading.Event()
_thread = None


def set_simas(simas):
    # iz camera.py
    global _latest
    with _lock:
        _latest = list(simas)

def make_packet(seq, simas):
    simas = simas[:MAX_SIMA]
    pkt = struct.pack(HDR, 2, 0, seq, len(simas))
    for sid, x_mm, y_mm in simas:
        pkt += struct.pack(ENT, sid, x_mm, y_mm)
    return pkt

def _sender_loop():
    interval = 1.0 / RATE
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(False)
    seq = 0
    next_t = time.perf_counter()

    while not _stop.is_set():
        with _lock:
            simas = list(_latest)

        pkt = make_packet(seq, simas)
        for addr in PICOS:
            try:
                s.sendto(pkt, addr)
            except OSError:
                pass
        seq += 1

        next_t += interval
        delay = next_t - time.perf_counter()        # moze i samo time.sleep(interval), ali i instrukcijama je potrebno vreme da se izvrse i ovako je precizno 200ms
        if delay > 0:
            time.sleep(delay)
        else:
            next_t = time.perf_counter()

    s.close()

def start_sender():
    global _thread
    if _thread and _thread.is_alive():
        return
    _stop.clear()
    _thread = threading.Thread(target=_sender_loop, daemon=True)
    _thread.start()

def stop_sender():
    _stop.set()
    if _thread:
        _thread.join(timeout=1)