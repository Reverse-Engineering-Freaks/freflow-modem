from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Self


class Instruction(Enum):
    UNDEFINED = 0x0000
    # Controls
    LIGHTNING_CONTROL = 0xA000
    LIGHTNING_CONTROL_2 = 0xA001
    SIGNAL_TEST = 0xA002
    SET_COLOR_TABLE = 0xA010
    # Settings
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

        data = self.LENGTH.to_bytes(2, "little")
        data += self.system_id.to_bytes(2, "little")
        data += self.unknown_0.to_bytes(2, "little")
        data += self.channel.to_bytes(2, "little")
        data += self._instruction().value.to_bytes(2, "little")
        data += self._variable_data_buffer()
        if len(data) < self.LENGTH:
            data += b"\x00" * (self.LENGTH - len(data))
        return data


@dataclass
class GenericMessage(MessageBase):
    """Generic Message"""

    instruction: Instruction
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
        instruction = Instruction(int.from_bytes(data[6:8], "little"))
        return cls(system_id, unknown_0, channal, instruction)

    def _instruction(self) -> Instruction:
        return self.instruction

    def _variable_data_buffer(self) -> bytes:
        return self.variable_data


@dataclass
class Color:
    red: int
    green: int
    blue: int

    @classmethod
    def from_normal_rgb(cls, red: int, green: int, blue: int) -> Self:
        """From normal RGB

        Args:
            red (int): Red (0-255)
            green (int): Green (0-255)
            blue (int): Blue (0-255)

        Returns:
            Self: Color instance
        """

        return cls(
            round(red / 255 * 100),
            round(green / 255 * 100),
            round(blue / 255 * 100),
        )

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

    def to_bytes(self) -> bytes:
        """To Bytes

        Returns:
            bytes: This instance as bytes
        """

        data = self.sequence_number.to_bytes(2, "little")
        flag = self.control_mode.value
        flag |= self.animation_mode.value << 2
        flag |= (1 if self.rf_controlled else 0) << 4
        data += flag.to_bytes()
        data += self.random_mode_sequence_number.to_bytes()
        data += self.color.to_bytes()
        data += self.animation_on_time.to_bytes()
        data += self.animation_off_time.to_bytes()
        data += self.brightness.to_bytes()
        return data


@dataclass
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
        for i in range(5):
            offset = i * 10
            controls.append(
                LightningControl.from_bytes(generic.variable_data[offset : offset + 10])
            )

        return cls(
            generic.system_id,
            generic.unknown_0,
            generic.channel,
            controls,
        )

    def _instruction(self) -> Instruction:
        return Instruction.LIGHTNING_CONTROL

    def _variable_data_buffer(self) -> bytes:
        data = b""
        for control in self.controls:
            data += control.to_bytes()
        return data


@dataclass
class LightningControlMessage2(LightningControlMessage):
    def _instruction(self) -> Instruction:
        return Instruction.LIGHTNING_CONTROL_2


@dataclass
class SignalErrorTestMessage(MessageBase):
    sequence_number: int

    def _instruction(self) -> Instruction:
        return Instruction.SIGNAL_TEST

    def _variable_data_buffer(self) -> bytes:
        data = b"\x00\x00"
        data += self.sequence_number.to_bytes()
        return data
