from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from io import BufferedReader, BufferedWriter
from typing import Self


class Instruction(Enum):
    COMMAND_A000 = 0xA000
    COMMAND_A002 = 0xA001
    COMMAND_A002 = 0xA002
    COMMAND_A010 = 0xA010
    COMMAND_A999 = 0xA999
    COMMAND_E002 = 0xE002
    COMMAND_E003 = 0xE003
    COMMAND_E021 = 0xE021


@dataclass
class Message(ABC):
    def __init__(self, system_id: int, instruction: Instruction) -> None:
        self.system_id = system_id
        self.instruction = instruction

    @abstractmethod
    def payload_buffer(self) -> bytes:
        # Length 0x003C
        buffer = b"\x3c\x00"
        buffer += self.system_id.to_bytes(2, "little")
        # unknown_0
        buffer += b"\x00\x00"
        buffer += self.instruction.value.to_bytes(2, "little")
