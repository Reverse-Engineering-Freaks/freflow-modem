from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Self


class Instruction(Enum):
    UNDEFINED = 0x0000
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

    @abstractmethod
    def _instruction() -> Instruction:
        """Instruction

        Returns:
            Instruction: Instruction value
        """

        pass

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
        data += self._instruction().value.to_bytes(2, "little")
        data += self._variable_data_buffer()
        return data


@dataclass
class GenericMessage(MessageBase):
    """Generic Message"""

    variable_data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        """From bytes

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
        return cls(system_id, unknown_0, channal, instruction)

    def _instruction() -> Instruction:
        return Instruction.UNDEFINED

    def _variable_data_buffer(self) -> bytes:
        return self.variable_data


@dataclass
class Color:
    red: int
    green: int
    blue: int

    def to_bytes(self) -> bytes:
        """To Bytes

        Returns:
            bytes: This instance as bytes
        """

        data = self.red.to_bytes()
        data += self.green.to_bytes()
        data += self.blue.to_bytes()
        return data


class ControlMode(Enum):
    SET_RF_CONTROLLED_ONLY = 0x00
    NORMAL = 0x01
    RESERVED = 0x02
    RANDOM = 0x03


class AnimationMode(Enum):
    NONE = 0x00
    BLINK = 0x01
    FADE = 0x02
    RESERVED = 0x03


@dataclass
class LightningControl:
    sequence_number: int
    control_mode: ControlMode
    animation_mode: AnimationMode
    rf_controlled: bool
    random_mode_sequence_number: int
    color: Color
    animation_on_time: int
    animation_off_time: int
    brightness: int

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        """From bytes

        Args:
            data (bytes): Data Bytes

        Returns:
            Self: Instance of this class
        """

        sequence_number = int.from_bytes(data[0:2], "little")
        flags = data[2]
        control_mode = ControlMode(flags & 0x03)
        animation_mode = AnimationMode(flags >> 2 & 0x03)
        rf_controlled = True if flags >> 4 & 0x03 != 0x00 else False
        random_mode_sequence_number = data[3]
        color = Color(
            data[4],
            data[5],
            data[6],
        )
        animation_on_time = data[7]
        animation_off_time = data[8]
        brightness = data[9]
        return cls(
            sequence_number,
            control_mode,
            animation_mode,
            rf_controlled,
            random_mode_sequence_number,
            color,
            animation_on_time,
            animation_off_time,
            brightness,
        )


class LightningControlMessage(MessageBase):
    controls: list[LightningControl]

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        """From bytes

        Args:
            data (bytes): Data Bytes

        Returns:
            Self: Instance of this class
        """

        generic = GenericMessage.from_bytes(data)

        controls: list[LightningControl] = []
        for i in range(6):
            offset = i * 10

            sequence_number = int.from_bytes(
                generic.variable_data[offset : offset + 2], "little"
            )
            flags = generic.variable_data[offset + 2]
            control_mode = ControlMode(flags & 0x03)
            animation_mode = AnimationMode(flags >> 2 & 0x03)
            rf_controlled = True if flags >> 4 & 0x03 != 0x00 else False
            random_mode_sequence_number = generic.variable_data[offset + 3]
            color = Color(
                generic.variable_data[offset + 4],
                generic.variable_data[offset + 5],
                generic.variable_data[offset + 6],
            )
            animation_on_time = generic.variable_data[offset + 7]
            animation_off_time = generic.variable_data[offset + 8]
            brightness = generic.variable_data[offset + 9]

            controls.append(
                LightningControl(
                    sequence_number,
                    control_mode,
                    animation_mode,
                    rf_controlled,
                    random_mode_sequence_number,
                    color,
                    animation_on_time,
                    animation_off_time,
                    brightness,
                )
            )

        return cls(
            generic.system_id,
            generic.unknown_0,
            generic.channel,
            generic.instruction,
            controls,
        )

    def _instruction() -> Instruction:
        return Instruction.COMMAND_A000

    def _variable_data_buffer(self) -> bytes:
        data = b""
        for control in self.controls:
            data = control.sequence_number.to_bytes(2, "little")
            flag = control.control_mode.value
            flag |= control.animation_mode.value << 2
            flag |= 1 if control.rf_controlled else 0 << 4
            data += flag.to_bytes()
            data += control.random_mode_sequence_number.to_bytes()
            data += control.color.to_bytes()
            data += control.animation_on_time.to_bytes()
            data += control.animation_off_time.to_bytes()
            data += control.brightness.to_bytes()
        return data


class LightningControlMessage2(LightningControlMessage):
    pass
