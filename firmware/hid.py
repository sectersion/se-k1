import time
import usb_hid

# HID keyboard device
keyboard = usb_hid.devices[0]

# Base HID keycodes (no Shift)
KEYCODE = {
    "a": 0x04, "b": 0x05, "c": 0x06, "d": 0x07,
    "e": 0x08, "f": 0x09, "g": 0x0A, "h": 0x0B,
    "i": 0x0C, "j": 0x0D, "k": 0x0E, "l": 0x0F,
    "m": 0x10, "n": 0x11, "o": 0x12, "p": 0x13,
    "q": 0x14, "r": 0x15, "s": 0x16, "t": 0x17,
    "u": 0x18, "v": 0x19, "w": 0x1A, "x": 0x1B,
    "y": 0x1C, "z": 0x1D,

    "1": 0x1E, "2": 0x1F, "3": 0x20, "4": 0x21,
    "5": 0x22, "6": 0x23, "7": 0x24, "8": 0x25,
    "9": 0x26, "0": 0x27,

    " ": 0x2C,
    "-": 0x2D, "=": 0x2E,
    "[": 0x2F, "]": 0x30,
    "\\": 0x31,
    ";": 0x33, "'": 0x34,
    "`": 0x35,
    ",": 0x36, ".": 0x37, "/": 0x38,

    "\n": 0x28,
}

# Characters requiring Shift
SHIFTED = {
    "!": ("1", 0x02),
    "@": ("2", 0x02),
    "#": ("3", 0x02),
    "$": ("4", 0x02),
    "%": ("5", 0x02),
    "^": ("6", 0x02),
    "&": ("7", 0x02),
    "*": ("8", 0x02),
    "(": ("9", 0x02),
    ")": ("0", 0x02),

    "_": ("-", 0x02),
    "+": ("=", 0x02),

    "{": ("[", 0x02),
    "}": ("]", 0x02),
    "|": ("\\", 0x02),

    ":": (";", 0x02),
    "\"": ("'", 0x02),
    "~": ("`", 0x02),

    "<": (",", 0x02),
    ">": (".", 0x02),
    "?": ("/", 0x02),
}


def send_key(code, modifier):
    report = bytes([modifier, 0, code, 0, 0, 0, 0, 0])
    keyboard.send_report(report)
    time.sleep_ms(5)

    # Release
    keyboard.send_report(b"\x00" * 8)
    time.sleep_ms(5)


def send_char(ch):
    if ch in KEYCODE:
        send_key(KEYCODE[ch], 0)
        return

    if ch in SHIFTED:
        base, mod = SHIFTED[ch]
        send_key(KEYCODE[base], mod)
        return

    if "A" <= ch <= "Z":
        send_key(KEYCODE[ch.lower()], 0x02)
        return


def type_string(s):
    for ch in s:
        send_char(ch)