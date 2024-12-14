from random import randint
from time import sleep

from freflow.message import Color, LightningControl, LightningControlMessage
from freflow.ez_radio_packet import EzRadioPacket
from freflow.transmitter import Transmitter

# payload = bytearray.fromhex(
#     """3C 00 FF FF 00 00 FF 00
#        00 A0 00 00 01 00 00 00 00 04 64 FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#     """
# )

frequency_start = int(922.4e6)
frequency_step = int(200e3)
channels = 1
for channel in range(channels):
    print("channel:", channel)
    frequency = frequency_start + frequency_step * channel
    tx = Transmitter("hackrf", int(4e6), int(frequency), 61)
    for i in range(100):
        print("iteration:", i)

    data = b""
    for j in range(2):
        iteration = i * 3 + j

        red = 100 if i % 3 == 0 else 0
        green = 100 if i % 3 == 1 else 0
        blue = 100 if i % 3 == 2 else 0

        message = LightningControlMessage(0xFFFF, 0x0000, 0x00FF)
        color = Color(red, green, blue)
        lightning_control = LightningControl()
        packet = EzRadioPacket(message.to_bytes(), 8)
        data += packet.to_bytes()

        tx.transmit(data)
        sleep(0.5)

    tx.close()
