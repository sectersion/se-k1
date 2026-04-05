from machine import Pin
import time
import pinlayout
# Build the keypad map once
_keypad_map = {
    Pin(pinlayout.BUTTON_1, Pin.IN, Pin.PULL_UP): "1",
    Pin(pinlayout.BUTTON_2, Pin.IN, Pin.PULL_UP): "2",
    Pin(pinlayout.BUTTON_3, Pin.IN, Pin.PULL_UP): "3",
    Pin(pinlayout.BUTTON_4, Pin.IN, Pin.PULL_UP): "4",
    Pin(pinlayout.BUTTON_5, Pin.IN, Pin.PULL_UP): "5",
    Pin(pinlayout.BUTTON_6, Pin.IN, Pin.PULL_UP): "6",
    Pin(pinlayout.BUTTON_7, Pin.IN, Pin.PULL_UP): "7",
    Pin(pinlayout.BUTTON_8, Pin.IN, Pin.PULL_UP): "8",
    Pin(pinlayout.BUTTON_9, Pin.IN, Pin.PULL_UP): "9",
    Pin(pinlayout.BUTTON_0, Pin.IN, Pin.PULL_UP): "0"
}

def read_pad(num_digits):
    pin_input = ""
    debounce_ms = 150
    last_press = time.ticks_ms()

    while True:
        for btn, digit in _keypad_map.items():
            if not btn.value():  # pressed
                now = time.ticks_ms()
                if time.ticks_diff(now, last_press) > debounce_ms:
                    pin_input += digit
                    last_press = now

                    if len(pin_input) == num_digits:
                        return int(pin_input)

                # wait for release
                while not btn.value():
                    time.sleep_ms(10)

        time.sleep_ms(10)