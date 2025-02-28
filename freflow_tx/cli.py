from colorsys import hsv_to_rgb
import fire
import logging
import signal
from time import sleep

from freflow_modem import (
    MessageBase,
    Color,
    ControlMode,
    AnimationMode,
    LightningControl,
    LightningControlMessage,
    LightningControlMessage2,
    TestSignalErrorMessage,
    EzRadioPacket,
    Transmitter,
)


class Cli:
    """FreFlow Modem CLI

    Args:
        dev (str): TX Device
        sr (int | float): TX Sampling Rate
        freq (int | float): TX Frequency
        gain (int | float): TX Gain (db)
        preamble_length (int): Preamble length in bytes
        log_level (str, optional): Log level. Defaults to "INFO". {CRITICAL|FATAL|ERROR|WARN|WARNING|INFO|DEBUG|NOTSET}

    Raises:
        ValueError: Argument `dev` must be str.
        ValueError: Argument `sr` must be int or float.
        ValueError: Argument `freq` must be int or float.
        ValueError: Argument `gain` must be int or float.
        ValueError: Argument `preamble_length` must be int.
    """

    @staticmethod
    def __config_logger(level: str) -> None:
        """Config logger

        Args:
            level (str): Log level
        """

        logging.basicConfig(
            level=level,
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        )

    def __init__(
        self,
        dev,
        sr,
        freq,
        gain,
        preamble_length=64,
        log_level="INFO",
    ) -> None:
        """FreFlow Modem CLI

        Args:
            dev (str): TX Device
            sr (int | float): TX Sampling Rate
            freq (int | float): TX Frequency
            gain (int | float): TX Gain (db)
            preamble_length (int): Preamble length in bytes
            log_level (str, optional): Log level. Defaults to "INFO". {CRITICAL|FATAL|ERROR|WARN|WARNING|INFO|DEBUG|NOTSET}

        Raises:
            ValueError: Argument `dev` must be str.
            ValueError: Argument `sr` must be int or float.
            ValueError: Argument `freq` must be int or float.
            ValueError: Argument `gain` must be int or float.
            ValueError: Argument `preamble_length` must be int.
        """

        Cli.__config_logger(log_level)
        self.__logger = logging.getLogger(__name__)

        if not isinstance(dev, str):
            raise ValueError("Argument `dev` must be str.")
        if not isinstance(sr, (int, float)):
            raise ValueError("Argument `sr` must be int or float.")
        if not isinstance(freq, (int, float)):
            raise ValueError("Argument `freq` must be int or float.")
        if not isinstance(gain, (int, float)):
            raise ValueError("Argument `gain` must be int or float.")
        if not isinstance(preamble_length, int):
            raise ValueError("Argument `preamble_length` must be int.")

        self.tx = Transmitter(dev, sr, freq, gain)

        self.preamble_length = preamble_length

        def signal_handler(signum, frame):
            self.__logger.info("SIGINT received. Exiting application.")
            tx_closed = self.tx.close()
            if tx_closed:
                exit(0)

        signal.signal(signal.SIGINT, signal_handler)

    def __transmit(self, messages: MessageBase | list[MessageBase]):
        if not isinstance(messages, list):
            messages = [messages]

        data = b""
        for message in messages:
            packet = EzRadioPacket(message.to_bytes(), self.preamble_length)
            iteration = (
                2
                if isinstance(
                    message,
                    (LightningControlMessage, LightningControlMessage2),
                )
                else 1
            )
            for _ in range(iteration):
                data += packet.to_bytes()
        self.tx.transmit(data)

    def light(self, red, green, blue, system_id=0xFFFF, channel=0xFF) -> None:
        """Light

        Args:
            red (int): Red (0-255)
            green (int): Green (0-255)
            blue (int): Blue (0-255)
            system_id (int, optional): System ID (0x0000-0xFFFF). Defaults to 0xFFFF.
            channel (int, optional): Channel (0x0000-0xFFFF). Defaults to 0xFF.
        """

        if not isinstance(system_id, int):
            raise ValueError("Argument `system_id` must be int.")
        if not isinstance(channel, int):
            raise ValueError("Argument `channel` must be int.")

        color = Color(
            int(red / 255 * 100), int(green / 255 * 100), int(blue / 255 * 100)
        )
        lightning_control = LightningControl(
            0,
            ControlMode.NORMAL,
            AnimationMode.NONE,
            True,
            0,
            color,
            0,
            0,
            255,
        )
        message = LightningControlMessage(
            system_id, 0x0000, channel, [lightning_control]
        )
        self.__transmit(message)
        self.tx.close()

    def light_interactive(self, system_id=0xFFFF, channel=0xFF) -> None:
        """Light (Interactive Mode)

        Transmit message by enter a comma separated RGB (0-255) and a line break.

        Args:
            system_id (int, optional): System ID (0x0000-0xFFFF). Defaults to 0xFFFF.
            channel (int, optional): Channel (0x0000-0xFFFF). Defaults to 0xFF.

        Raises:
            ValueError: Argument `system_id` must be int.
            ValueError: Argument `channel` must be int.
            ValueError: Comma separated values length must be 3.
        """

        if not isinstance(system_id, int):
            raise ValueError("Argument `system_id` must be int.")
        if not isinstance(channel, int):
            raise ValueError("Argument `channel` must be int.")

        i = 0
        while True:
            rgb = input("Enter comma separated RGB (0-255): ").split(",")
            if len(rgb) != 3:
                raise ValueError("Comma separated values length must be 3.")
            red, green, blue = rgb
            red, green, blue = int(red), int(green), int(blue)
            color = Color.from_normal_rgb(red, green, blue)
            lightning_control = LightningControl(
                i << 2,
                ControlMode.NORMAL,
                AnimationMode.NONE,
                True,
                0,
                color,
                0,
                0,
                255,
            )
            message = LightningControlMessage(
                system_id, 0x0000, channel, [lightning_control]
            )
            self.__transmit(message)
            i += 1

    def test_sig_err(self, system_id=0xFFFF, channel=0xFF) -> None:
        """Test Signal Error

        Green: No Error (0%)
        Blue: Few Error (0% < error <= 5%)
        Purple: Many Error (5% < error <= 20%)
        Red: Too Many Error (20% < error)

        Args:
            system_id (int, optional): System ID (0x0000-0xFFFF). Defaults to 0xFFFF.
            channel (int, optional): Channel (0x0000-0xFFFF). Defaults to 0xFF.
        """

        if not isinstance(system_id, int):
            raise ValueError("Argument `system_id` must be int.")
        if not isinstance(channel, int):
            raise ValueError("Argument `channel` must be int.")

        messages: list[LightningControlMessage] = []
        for i in range(1, 101):
            messages.append(TestSignalErrorMessage(system_id, 0x0000, channel, i))
        self.__transmit(messages)
        self.tx.close()

    def demo_gaming(self, system_id=0xFFFF, channel=0xFF) -> None:
        """The `Gaming` demonstration

        Args:
            system_id (int, optional): System ID (0x0000-0xFFFF). Defaults to 0xFFFF.
            channel (int, optional): Channel (0x0000-0xFFFF). Defaults to 0xFF.
        """

        if not isinstance(system_id, int):
            raise ValueError("Argument `system_id` must be int.")
        if not isinstance(channel, int):
            raise ValueError("Argument `channel` must be int.")

        i = 0
        while True:
            red, green, blue = hsv_to_rgb(i / 9, 1.0, 1.0)
            red, green, blue = int(255 * red), int(255 * green), int(255 * blue)
            color = Color.from_normal_rgb(red, green, blue)

            lightning_control = LightningControl(
                i << 2,
                ControlMode.NORMAL,
                AnimationMode.NONE,
                True,
                0,
                color,
                0,
                0,
                255,
            )
            message = LightningControlMessage(
                system_id, 0x0000, channel, [lightning_control]
            )
            self.__transmit(message)
            i = (i + 1) % 9
            sleep(0.01)


def main() -> None:
    fire.Fire(Cli)


if __name__ == "__main__":
    main()
