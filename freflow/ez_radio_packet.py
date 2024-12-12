from dataclasses import dataclass
from fastcrc import crc16


@dataclass
class EzRadioPacket:
    payload: bytes
    preamble_length_bytes: int = 3
    sync_word: bytes = b"\x6a\x55\xad\xab"

    def to_bytes(self):
        buffer = b"\x55" * self.preamble_length_bytes
        buffer += self.sync_word
        buffer += len(self.payload).to_bytes()
        buffer += self.payload
        buffer += crc16.umts(self.payload).to_bytes(2, "big")
        return buffer
