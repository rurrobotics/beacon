import socket
import time
import struct

# slanje paketa i testiranje koliko je izgubljeno

def run(stop):
    PICO = ("192.168.137.17", 5005)
    RATE = 20
    N = RATE * 15   # broj paketa je brzina * 15s trajanje slanja
    PAYLOAD = 16

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        send_errors = 0
        pad = b"x" * PAYLOAD
        interval = 1.0 / RATE
        start = time.perf_counter()

        sent = 0
        for seq in range(N):
            if stop.is_set():
                break
            try:
                sock.sendto(struct.pack("<BI", 0, seq) + pad, PICO)
            except OSError:
                send_errors += 1
            sent += 1

            target = start + (seq + 1) * interval
            delay = target - time.perf_counter()
            if delay > 0 and stop.wait(delay):   # sleeps, but wakes on stop
                break

        if stop.is_set():
            return

        elapsed = time.perf_counter() - start
        stop.wait(0.3)

        sock.settimeout(0.5)  # da ne freezuje script
        stats = None
        for _ in range(10):
            if stop.is_set():
                return
            sock.sendto(struct.pack("<BI", 1, 0) + pad, PICO)
            try:
                data, _ = sock.recvfrom(64)
                stats = data.decode().split(",")
                break
            except socket.timeout:
                pass

        if stats:
            got = int(stats[0])
            max_gap = int(stats[2])
            print(f"sent {N} in {elapsed:.2f}s ({N/elapsed:.0f} pkt/s), send errors: {send_errors}")
            print(f"received {got}, lost {N-got} ({(N-got)/N*100:.2f}%)")
            print(f"longest gap between packets {max_gap}ms "
                  f"({max(0, round(max_gap / (interval * 1000)) - 1)} lost in a row)")
        else:
            print("No stats reply from Pico")
    finally:
        sock.close()