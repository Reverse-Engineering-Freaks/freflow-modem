from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Self


class Instruction(Enum):
    COMMAND_A000 = 0xA000
    COMMAND_A001 = 0xA001
    COMMAND_A002 = 0xA002
    COMMAND_A010 = 0xA010
    COMMAND_A999 = 0xA999
    COMMAND_E002 = 0xE002
    COMMAND_E003 = 0xE003
    COMMAND_E021 = 0xE021


@dataclass
class MessageBase(ABC):
    """Message Base Class"""

    LENGTH = 60

    system_id: int
    unknown_0: int
    channel: int
    instruction: Instruction
    sequence_number: int

    @abstractmethod
    def _variable_data_buffer() -> bytes:
        """Variable Data Buffer

        Returns:
            bytes: Valiable Data Buffer
        """

        pass

    def to_bytes(self) -> bytes:
        """To Bytes

        Returns:
            bytes: This instance as bytes
        """

        data = self.LENGTH
        data += self.system_id.to_bytes(2, "little")
        data += self.unknown_0.to_bytes(2, "little")
        data += self.channel.to_bytes(2, "little")
        data += self.instruction.value.to_bytes(2, "little")
        data += self.sequence_number.to_bytes(2, "little")
        data += self._variable_data_buffer()


@dataclass
class GenericMessage(MessageBase):
    """Generic Message"""

    variable_data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        """Read

        Args:
            data (bytes): Data Bytes

        Returns:
            Self: Instance of this class
        """

        system_id = int.from_bytes(data[0:2], "little")
        unknown_0 = int.from_bytes(data[2:4], "little")
        channal = int.from_bytes(data[4:6], "little")
        instruction_int = int.from_bytes(data[6:8], "little")
        instruction = Instruction(instruction_int)
        sequence_number = int.from_bytes(data[8:10], "little")
        return cls(system_id, unknown_0, channal, instruction, sequence_number)

    def _optional_data_buffer(self) -> bytes:
        return self.variable_data

class CommandA001Message:
    pass
