from machine import Pin, SPI
import time
import machine
import button_manager
import flash
import pinlayout
from tpm import SLB9670
import uhashlib
from hid import type_string


def init_flash():
    global flash0
    flash0 = flash.FlashStorage(spi=pinlayout.spi, cs_pin=pinlayout.flash_cs)
    return flash0


def init_tpm():
    global tpm
    tpm = SLB9670(spi_bus=pinlayout.spi, cs_pin=pinlayout.tpm_cs, irq_pin=pinlayout.tpm_irq)
    return tpm


def hash_pin(pin_str: str) -> bytes:
    # SHA256(unique_id, pin)
    h = uhashlib.sha256()
    h.update(machine.unique_id())
    h.update(pin_str.encode())
    return h.digest()[:16]


def read_id():
    return button_manager.read_pad(4)


def read_pin():
    return button_manager.read_pad(6)



def flash_read_record(record_id):
    addr = flash0.find_record_by_id(record_id)
    return flash0.read_record(addr)


def tpm_authorize(record, pin_input, master_key_handle):
    # check pin
    if hash_pin(pin_input) != record["encrypted_pin"]:
        return None

    # tpm decrypt
    tpm.start_hmac_session()
    key_handle = tpm.load_master_key(master_key_handle)
    return tpm.decrypt_with_master(record["encrypted_password"], key_handle)


def output_secret(secret):
    if secret is None:
        print("debug.InvalidPIN")
    else:
        type_string(secret)

def handle_user_session():
    uid = read_id()
    rec = flash_read_record(uid)
    pin = read_pin()

    MASTER_KEY = 0x81000001
    secret = tpm_authorize(rec, pin, MASTER_KEY)
    output_secret(secret)





def main_loop():
    while True:
        handle_user_session()


def main():
    init_flash()
    init_tpm()
    main_loop()


if __name__ == "__main__":
    main()