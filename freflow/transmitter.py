from gnuradio import gr, blocks, digital
import numpy as np
from python_hackrf import pyhackrf
from SoapySDR import SOAPY_SDR_TX, SOAPY_SDR_CF32, Device
from time import sleep


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
            do_unpack=False,
        )

        self.sink = blocks.vector_sink_c()

        self.tb.connect(self.src, self.gmsk_mod, self.sink)

        self.tx_stream = self.sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CF32)
        self.mtu = self.sdr.getStreamMTU(self.tx_stream)
        self.buffer_wait = self.mtu / tx_sampling_rate

        self.sdr.activateStream(self.tx_stream)
        # sleep(1)

    def transmit(self, data: bytes) -> int:
        """Transmit data

        Args:
            data (bytes): Data
        """

        # data *= 2

        data_bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        self.src.set_data(data_bits.tolist())
        self.sink.reset()
        self.tb.run()
        modulated = np.array(self.sink.data(), dtype=np.complex64)
        # modulated = np.pad(modulated, (0, self.mtu * 4))

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
        # self.sdr.pyhackrf_close()
        # sleep(2)
        self.sdr.deactivateStream(self.tx_stream)
        self.sdr.closeStream(self.tx_stream)
