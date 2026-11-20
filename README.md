# Beacon - Eurobot 2027

[Srpski](README.sr.md)

The `beacon` folder contains all of the Python code (the `beacon` package) for the Beacon at the Eurobot 2027 competition.

## Installation and running

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Running:

```sh
beacon
# or
python -m beacon
```

## Camera

First, the camera's perspective has to be transformed so that pixels match the table's millimeter grid. This is done using the IDs on the table.

The IDs are ArUco tags, and they are detected using the OpenCV library.

During the last 15 seconds, the camera detects the positions of the opponent's SIMAs by finding their IDs and converting the detected pixels into millimeters on the table. The data read from the camera is sent to the SIMAs using the communication described below.

## Communication between the Beacon and the SIMAs

UDP was chosen over TCP for speed. Although there is a risk of packet loss, it doesn't matter much to us, because packets are sent every 200 ms.

The RPi5 sends the Pico information about all SIMAs on the table. The number of SIMAs isn't known in advance: one team might have 4, another none, and so on. For that reason, a maximum number of SIMAs that can be on the table has to be defined, and during the match the RPi5 sends entries for as many SIMAs as the camera detects IDs.

Packets are packed into bytes with ```struct.pack()``` and ```struct.unpack()``` in little-endian format (it doesn't really matter, but this is how the RPi5 and the Pico pack data), and they consist of two parts: a Header and Entries.

### Header ("<BBIB")
| Field | Meaning | Format | Bytes |  |
| --- | --- | --- | --- | --- |
| ```type``` | Packet type | Unsigned Byte (B) | 1 | Distinguishes packet types in case we send more kinds of packets to the Pico in the future. For SIMA coordinates it is 2 |
| ```version``` | Version | Unsigned Byte (B) | 1 | Format version, so that if something is added in the future, the Pico knows to discard the old format |
| ```seq``` | Packet sequence number | Unsigned Integer (I) | 4 | Old packets and duplicates are ignored |
| ```n``` | Number of SIMAs | Unsigned Byte (B) | 1 | How many SIMAs the Beacon sees |

### Entry ("<Bhh")
| Field | Meaning | Format | Bytes |  |
| --- | --- | --- | --- | --- |
| ```id``` | SIMA ID | Unsigned Byte (B) | 1 | Which SIMA it is |
| ```x_mm``` | X coordinate [mm] | Signed Short (h) | 2 | 0 - 3000 mm |
| ```y_mm``` | Y coordinate [mm] | Signed Short (h) | 2 | 0 - 2000 mm |

The total packet size is 7 + n * 5 bytes. The maximum number of opponent SIMAs that can be on the table is 6, so the largest packet the RPi5 sends to the Pico is 37 bytes (64 bytes when rounded up).
