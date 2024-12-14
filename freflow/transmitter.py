from gnuradio import gr, blocks, digital
import numpy as np
from SoapySDR import SOAPY_SDR_TX, SOAPY_SDR_CF32, Device


class Transmitter:
    __SYMBOLS_PER_SECOND = 80000
    __MSK_BT = 0.5

    def __init__(
        self,
        tx_device: str,
        tx_sampling_rate: int,
        tx_frequency: float,
        tx_gain: int,
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
        self.sdr.setGain(SOAPY_SDR_TX, 0, tx_gain)

        self.tb = gr.top_block()

        self.src = blocks.vector_source_b([])

        self.samples_per_symbol = self.tx_sampling_rate // self.__SYMBOLS_PER_SECOND
        self.bt = self.__MSK_BT
        self.gmsk_mod = digital.gmsk_mod(
            samples_per_symbol=self.samples_per_symbol,
            bt=self.bt,
            verbose=False,
            do_unpack=True,
        )

        self.sink = blocks.vector_sink_c()

        self.tb.connect(self.src, self.gmsk_mod, self.sink)

        self.tx_stream = self.sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CF32)
        self.mtu = self.sdr.getStreamMTU(self.tx_stream)
        self.buffer_wait = self.mtu / tx_sampling_rate

        self.sdr.activateStream(self.tx_stream)

    def transmit(self, data: bytes) -> int:
        """Transmit data

        Args:
            data (bytes): Data

        Returns:
            int: Sent data length
        """

        self.src.set_data(bytearray(data))
        self.sink.reset()
        self.tb.run()
        modulated = np.array(self.sink.data(), dtype=np.complex64)

        sent = 0
        while sent < len(modulated):
            chunk = modulated[sent : sent + self.mtu]
            if len(chunk) < self.mtu:
                chunk = np.pad(chunk, (0, self.mtu - len(chunk)))
            status = self.sdr.writeStream(
                self.tx_stream, [chunk], chunk.size, timeoutUs=1000000
            )
            if status.ret != chunk.size:
                print(f"Warning: Only {status.ret} of {len(chunk)} samples sent")
                return -1
            sent += status.ret
        return sent

    def close(self) -> None:
        """Close"""
        self.sdr.deactivateStream(self.tx_stream)
        self.sdr.closeStream(self.tx_stream)
