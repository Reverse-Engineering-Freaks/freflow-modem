from gnuradio import gr, blocks, digital
import numpy as np
from SoapySDR import SOAPY_SDR_TX, SOAPY_SDR_CF32, Device
from time import sleep


class Transmitter:
    __SYMBOLS_PER_SECOND = 80000
    __MSK_BT = 0.5

    def __init__(
        self,
        tx_device: str,
        tx_frequency: float,
        tx_sampling_rate: int,
        tx_gain: int,
        if_gain: int,
    ) -> None:
        """Constructor

        Args:
            tx_device (str): TX Device
            tx_frequency (float): TX Frequency
            tx_sampling_rate (int): TX Sampling Rate
            tx_gain (int): TX Gain
        """

        self.tx_sampling_rate = tx_sampling_rate

        self.sdr = Device(dict(driver=tx_device))
        self.sdr.setFrequency(SOAPY_SDR_TX, 0, tx_frequency)
        self.sdr.setSampleRate(SOAPY_SDR_TX, 0, self.tx_sampling_rate)

        if self.sdr.getDriverKey() == "HackRF":
            self.sdr.setGain(SOAPY_SDR_TX, 0, "VGA", min(max(if_gain, 0.0), 47.0))
            self.sdr.setGain(SOAPY_SDR_TX, 0, "AMP", 1 if tx_gain > 0 else 0)
        else:
            self.sdr.setGain(SOAPY_SDR_TX, 0, tx_gain)

        self.tb = gr.top_block()

        self.src = blocks.vector_source_b([])

        self.samples_per_symbol = tx_sampling_rate // self.__SYMBOLS_PER_SECOND
        self.bt = self.__MSK_BT
        self.gmsk_mod = digital.gmsk_mod(
            samples_per_symbol=self.samples_per_symbol,
            bt=self.bt,
            verbose=False,
            do_unpack=False,
        )

        self.sink = blocks.vector_sink_c()

        self.tb.connect(self.src, self.gmsk_mod, self.sink)

        self.tx_stream = self.sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CF32)
        self.mtu = self.sdr.getStreamMTU(self.tx_stream)

        self.sdr.activateStream(self.tx_stream)
        sleep(0.1)

    def transmit(self, data: bytes) -> None:
        """Transmit data

        Args:
            data (bytes): Data
        """

        data = data + b"\x00" * 16

        data_bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        self.src.set_data(data_bits.tolist())
        self.sink.reset()
        self.tb.run()
        modulated = np.array(self.sink.data(), dtype=np.complex64)

        for i in range(0, len(modulated), self.mtu):
            chunk = modulated[i : i + self.mtu]
            if len(chunk) < self.mtu:
                chunk = np.pad(chunk, (0, self.mtu - len(chunk)))

            rc = self.sdr.writeStream(self.tx_stream, [chunk], self.mtu)
            if rc.ret != len(chunk):
                print(f"Warning: Only {rc.ret} of {len(chunk)} samples sent")

    def close(self) -> None:
        """Close"""
        sleep(2)
        self.sdr.deactivateStream(self.tx_stream)
        self.sdr.closeStream(self.tx_stream)
