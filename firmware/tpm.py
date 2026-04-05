from machine import Pin, SPI
import time


class SLB9670:
    def __init__(self, spi_bus, cs_pin, irq_pin):
        # SPI instance created outside (shared SPI bus)
        self.spi = spi_bus

        # Chip-select pin (output)
        self.cs = cs_pin
        self.cs.init(Pin.OUT, value=1)

        # IRQ pin (input)
        self.irq = irq_pin
        self.irq.init(Pin.IN)

        # Optional: track ready state
        self.ready = False

        # Perform TPM startup checks or initialization
        self._startup_sequence()

    def _startup_sequence(self):
        # Wait for TPM to assert IRQ or become ready
        # Real hardware: poll IRQ or read status until operational
        time.sleep_ms(10)
        self.ready = True

    def _select(self):
        self.cs(0)

    def _deselect(self):
        self.cs(1)

    def _transfer(self, tx_data, rx_length=0):
        # Send bytes to TPM and optionally read back response
        self._select()
        self.spi.write(tx_data)
        result = None
        if rx_length > 0:
            result = self.spi.read(rx_length)
        self._deselect()
        return result

    def wait_irq(self, timeout_ms=1000):
        # Wait for IRQ to trigger a ready signal
        start = time.ticks_ms()
        while not self.irq.value():
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                return False
            time.sleep_ms(1)
        return True

    def send_command(self, command_bytes):
        # Wrap SPI send + IRQ wait + response read
        if not self.ready:
            return None

        self._transfer(command_bytes)
        if not self.wait_irq():
            return None

        # Placeholder: always read a fixed response size
        # Replace with TPM header parsing
        response = self._transfer(b"", rx_length=32)
        return response

    def tpm_selftest(self):
        # Send TPM selftest command (placeholder)
        return self.send_command(b"\x00\x00\x00\x00")

    def read_random(self, num_bytes=16):
        # Placeholder random-number command
        # Replace with correct TPM2_GetRandom command structure
        response = self.send_command(b"\x01\x00" + bytes([num_bytes]))
        return response

    def flush_handles(self):
        # Placeholder TPM2_FlushContext command
        return self.send_command(b"\x02\x00\x00\x00")

    def is_ready(self):
        return self.ready