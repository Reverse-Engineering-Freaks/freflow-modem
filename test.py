from random import randint
from time import sleep

from freflow.ez_radio_packet import EzRadioPacket
from freflow.transmitter import Transmitter

payload = bytearray.fromhex(
    """3C 00 FF FF 00 00 FF 00
       00 A0 00 00 01 00 00 00 00 04 64 FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    """
)

tx = Transmitter("hackrf", int(4e6), int(922.4e6), 61)
for i in range(100):
    print(i)

    data = b""
    for j in range(2):
        iteration = i * 3 + j
        payload[10] = iteration & 0xFF
        payload[11] = iteration >> 8 & 0xFF

        payload[14] = 100 if i % 3 == 0 else 0
        payload[15] = 100 if i % 3 == 1 else 0
        payload[16] = 100 if i % 3 == 2 else 0
        print(payload[14], payload[15], payload[16])

        packet = EzRadioPacket(bytes(payload), 8)
        data += packet.to_bytes()

    tx.transmit(data)
    sleep(0.5)

tx.close()
