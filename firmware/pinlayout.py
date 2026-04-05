
from machine import Pin

#spi
SPI_BUS = 1
SPI_SCK = 36
SPI_MISO = 37
SPI_MOSI = 35

#individial cs
FLASH_CS = 33
TPM_CS = 34

#buttons
BUTTON_1 = 1
BUTTON_2 = 2
BUTTON_3 = 3
BUTTON_4 = 4
BUTTON_5 = 5
BUTTON_6 = 6
BUTTON_7 = 7
BUTTON_8 = 8
BUTTON_9 = 9
BUTTON_0 = 10

#tpm
TPM_IRQ = 38

from machine import Pin, SPI

# SPI pins
spi = SPI(
    SPI_BUS,
    baudrate=4_000_000,
    sck=Pin(SPI_SCK),
    mosi=Pin(SPI_MOSI),
    miso=Pin(SPI_MISO),
)

# Chip-select pins
flash_cs = Pin(FLASH_CS, Pin.OUT, value=1)
tpm_cs = Pin(TPM_CS, Pin.OUT, value=1)

# Buttons
button_1 = Pin(BUTTON_1, Pin.IN, Pin.PULL_UP)
button_2 = Pin(BUTTON_2, Pin.IN, Pin.PULL_UP)
button_3 = Pin(BUTTON_3, Pin.IN, Pin.PULL_UP)
button_4 = Pin(BUTTON_4, Pin.IN, Pin.PULL_UP)
button_5 = Pin(BUTTON_5, Pin.IN, Pin.PULL_UP)
button_6 = Pin(BUTTON_6, Pin.IN, Pin.PULL_UP)
button_7 = Pin(BUTTON_7, Pin.IN, Pin.PULL_UP)
button_8 = Pin(BUTTON_8, Pin.IN, Pin.PULL_UP)
button_9 = Pin(BUTTON_9, Pin.IN, Pin.PULL_UP)
button_0 = Pin(BUTTON_0, Pin.IN, Pin.PULL_UP)

# TPM IRQ pin
tpm_irq = Pin(TPM_IRQ, Pin.IN)