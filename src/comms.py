import socket
import time
import struct

# slanje 5000 paketa i testiranje koliko je izgubljeno

def send_udp_data():
    PICO = ("192.168.137.17", 5005)
    RATE = 20
    N = RATE * 15   # broj paketa je brzina * 15s trajanje slanja
    PAYLOAD = 16

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(None)

    send_errors = 0
    pad = b"x" * PAYLOAD
    interval = 1.0 / RATE
    start = time.perf_counter()

    for seq in range(N):
        try:
            sock.sendto(struct.pack("<BI", 0, seq) + pad, PICO)
        except OSError:
            send_errors += 1

        target = start + (seq + 1) * interval
        while time.perf_counter() < target:
            time.sleep(0.001)

    elapsed = time.perf_counter() - start
    time.sleep(0.3)

    sock.settimeout(0.5) # da ne freezuje script
    stats = None
    for _ in range(10):
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
        print(f"sent {N} in {elapsed:.2f}s ({N/elapsed:.0f} pkt/s)")
        print(f"recieved {got}, lost {N-got} ({100-(N-got)/N*100:.2f}%)")
        print(f"longest gap between packets {max_gap}ms ({max(0, round(max_gap / (interval * 1000)) - 1)} lost in a row)")
    else:
        print("No stats reply from Pico")
