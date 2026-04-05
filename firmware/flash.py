from machine import Pin, SPI
import time
import struct

class FlashStorage:
    FLASH_SIZE = 2 * 1024 * 1024      # 2MB total
    SECTOR_SIZE = 4096                 # 4KB sectors
    PAGE_SIZE = 256                    # 256 byte pages
    BLOCK_SIZE_32K = 32 * 1024        # 32KB blocks
    BLOCK_SIZE_64K = 64 * 1024        # 64KB blocks
    

    CMD_WRITE_ENABLE = 0x06
    CMD_WRITE_DISABLE = 0x04
    CMD_READ_STATUS = 0x05
    CMD_WRITE_STATUS = 0x01
    CMD_READ_DATA = 0x03
    CMD_FAST_READ = 0x0B
    CMD_PAGE_PROGRAM = 0x02
    CMD_SECTOR_ERASE = 0x20
    CMD_BLOCK_ERASE_32K = 0x52
    CMD_BLOCK_ERASE_64K = 0xD8
    CMD_CHIP_ERASE = 0xC7
    CMD_POWER_DOWN = 0xB9
    CMD_RELEASE_POWER_DOWN = 0xAB
    CMD_READ_ID = 0x9F


    STATUS_BUSY = 0x01
    STATUS_WEL = 0x02  # Write Enable Latch
    

    RECORD_SIZE = 52
    OFFSET_ID = 0
    OFFSET_ENC_PASSWORD = 4
    OFFSET_ENC_PIN = 20
    OFFSET_MAC = 36
    
    SIZE_ID = 4
    SIZE_ENC_PASSWORD = 16
    SIZE_ENC_PIN = 16
    SIZE_MAC = 16
    

    MAX_RECORDS = 312
    RECORDS_PER_SECTOR = SECTOR_SIZE // RECORD_SIZE  # 78 records per sector
    
    def __init__(self, spi, cs_pin):
        self.spi = spi
        self.cs = cs_pin
        self.cs.value(1)  # CS high = inactive
        
        # Wake up flash if it was in power-down
        self._release_power_down()
        time.sleep_ms(10)
        
        # Verify chip ID
        chip_id = self.read_chip_id()
        print(f"Chip ID: {chip_id.hex()}")
        
        if chip_id[0] != 0xEF:  # Winbond manufacturer ID
            print("Unexpected manufacturer ID")
    
    def _select(self):
        self.cs.value(0)
        time.sleep_us(1)  # Small delay for CS setup time
    
    def _deselect(self):
        time.sleep_us(1)  # Hold time
        self.cs.value(1)
    
    def _wait_ready(self, timeout_ms=1000):
        start = time.ticks_ms()
        
        while True:
            status = self._read_status()
            
            if not (status & self.STATUS_BUSY):
                return True
            
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                print("Timeout waiting for ready")
                return False
            
            time.sleep_ms(1)
    
    def _read_status(self):
        self._select()
        self.spi.write(bytes([self.CMD_READ_STATUS]))
        status = self.spi.read(1)
        self._deselect()
        return status[0]
    
    def _write_enable(self):
        self._select()
        self.spi.write(bytes([self.CMD_WRITE_ENABLE]))
        self._deselect()
        time.sleep_us(10)
    
    def _write_disable(self):
        self._select()
        self.spi.write(bytes([self.CMD_WRITE_DISABLE]))
        self._deselect()
    
    def _release_power_down(self):
        self._select()
        self.spi.write(bytes([self.CMD_RELEASE_POWER_DOWN]))
        self._deselect()
    
    def read_chip_id(self):
        self._select()
        self.spi.write(bytes([self.CMD_READ_ID]))
        chip_id = self.spi.read(3)
        self._deselect()
        return chip_id
    
    def read(self, address, length):
        if address + length > self.FLASH_SIZE:
            raise ValueError(f"Read beyond flash size (0x{address:06X} + {length})")
        
        self._wait_ready()
        
        self._select()
        
        # Send read command + 24-bit address
        cmd = bytes([
            self.CMD_READ_DATA,
            (address >> 16) & 0xFF,  # A23-A16
            (address >> 8) & 0xFF,   # A15-A8
            address & 0xFF           # A7-A0
        ])
        self.spi.write(cmd)
        
        data = self.spi.read(length)
        
        self._deselect()
        return data
    
    def write(self, address, data):
        if isinstance(data, str):
            data = data.encode()
        
        if address + len(data) > self.FLASH_SIZE:
            raise ValueError(f"Write beyond flash size")
        
        offset = 0
        
        while offset < len(data):
            # Calculate how much we can write in this page
            page_addr = address + offset
            page_offset = page_addr % self.PAGE_SIZE
            bytes_in_page = min(self.PAGE_SIZE - page_offset, len(data) - offset)
            
            # Write this chunk
            chunk = data[offset:offset + bytes_in_page]
            if not self._write_page(page_addr, chunk):
                return False
            
            offset += bytes_in_page
        
        return True
    
    def _write_page(self, address, data):
        if len(data) > self.PAGE_SIZE:
            raise ValueError("Data exceeds page size")
        
        # Must erase before writing (or data will be anded)
        self._wait_ready()
        self._write_enable()
        
        self._select()
        
        # Send page program command + address + data
        cmd = bytes([
            self.CMD_PAGE_PROGRAM,
            (address >> 16) & 0xFF,
            (address >> 8) & 0xFF,
            address & 0xFF
        ])
        self.spi.write(cmd)
        self.spi.write(data)
        
        self._deselect()
        
        # Wait for write to complete
        if not self._wait_ready(timeout_ms=100):
            print(f"Page write timeout at 0x{address:06X}")
            return False
        
        return True
    
    def erase_sector(self, address):
        # Align to sector boundary
        sector_addr = (address // self.SECTOR_SIZE) * self.SECTOR_SIZE
        
        print(f"Erasing sector at 0x{sector_addr:06X}")
        
        self._wait_ready()
        self._write_enable()
        
        self._select()
        
        cmd = bytes([
            self.CMD_SECTOR_ERASE,
            (sector_addr >> 16) & 0xFF,
            (sector_addr >> 8) & 0xFF,
            sector_addr & 0xFF
        ])
        self.spi.write(cmd)
        
        self._deselect()
        
        # Erase takes ~45-400ms
        if not self._wait_ready(timeout_ms=500):
            print("Sector erase timeout")
            return False
        
        print("Sector erased")
        return True
    
    def erase_chip(self):
        print("Erasing entire chip")
        
        self._wait_ready()
        self._write_enable()
        
        self._select()
        self.spi.write(bytes([self.CMD_CHIP_ERASE]))
        self._deselect()
        
        # Chip erase takes 6-20 seconds
        print("Waiting for chip erase (this may take 20 seconds)")
        if not self._wait_ready(timeout_ms=25000):
            print("Chip erase timeout")
            return False
        
        print("Chip erased")
        return True

    
    def get_record_address(self, slot):
        if slot >= self.MAX_RECORDS:
            raise ValueError(f"Slot {slot} exceeds max {self.MAX_RECORDS}")
        
        return slot * self.RECORD_SIZE
    
    def find_record_by_id(self, target_id):
        if isinstance(target_id, str):
            target_id = target_id.encode()
        
        if len(target_id) != self.SIZE_ID:
            raise ValueError("ID must be 4 bytes")
        
        for slot in range(self.MAX_RECORDS):
            address = self.get_record_address(slot)
            
            # Read just the ID field (first 4 bytes)
            record_id = self.read(address, self.SIZE_ID)
            
            # Check for match
            if record_id == target_id:
                return address
            
            # Empty slot (erased flash)
            if record_id == b'\xFF\xFF\xFF\xFF':
                break  # No more records beyond this point
        
        return None
    
    def find_empty_slot(self):
        for slot in range(self.MAX_RECORDS):
            address = self.get_record_address(slot)
            record_id = self.read(address, self.SIZE_ID)
            
            if record_id == b'\xFF\xFF\xFF\xFF':
                return slot
        
        return None  # Flash full
    
    def read_record(self, address):
        data = self.read(address, self.RECORD_SIZE)
        
        return {
            'id': data[self.OFFSET_ID:self.OFFSET_ID + self.SIZE_ID],
            'encrypted_password': data[self.OFFSET_ENC_PASSWORD:self.OFFSET_ENC_PASSWORD + self.SIZE_ENC_PASSWORD],
            'encrypted_pin': data[self.OFFSET_ENC_PIN:self.OFFSET_ENC_PIN + self.SIZE_ENC_PIN],
            'mac': data[self.OFFSET_MAC:self.OFFSET_MAC + self.SIZE_MAC]
        }
    
    def write_record(self, slot, record_id, encrypted_password, encrypted_pin, mac):
        # Validate inputs
        if len(record_id) != self.SIZE_ID:
            raise ValueError("ID must be 4 bytes")
        if len(encrypted_password) != self.SIZE_ENC_PASSWORD:
            raise ValueError("Encrypted password must be 16 bytes")
        if len(encrypted_pin) != self.SIZE_ENC_PIN:
            raise ValueError("Encrypted PIN must be 16 bytes")
        if len(mac) != self.SIZE_MAC:
            raise ValueError("MAC must be 16 bytes")
        
        address = self.get_record_address(slot)
        
        # Check if we need to erase the sector
        sector_start = (address // self.SECTOR_SIZE) * self.SECTOR_SIZE
        
        # Simple check: if first byte isn't 0xFF, we need to erase
        first_byte = self.read(address, 1)
        if first_byte[0] != 0xFF:
            print(f"Slot {slot} not empty, erasing sector...")
            if not self.erase_sector(address):
                return False
        
        # Assemble record
        record = record_id + encrypted_password + encrypted_pin + mac
        
        print(f"Writing record to slot {slot} (addr: 0x{address:06X})")
        
        # Write the record
        if not self.write(address, record):
            print("Write failed")
            return False
        
        # Verify
        written = self.read(address, self.RECORD_SIZE)
        if written != record:
            print("Verification failed")
            return False
        
        print(f"Record written and verified")
        return True
    
    def delete_record(self, address):
        deletion_marker = b'\x00\x00\x00\x00' + (b'\xFF' * (self.RECORD_SIZE - 4))
        return self.write(address, deletion_marker)
    
    def read_encrypted_password(self, record_id):
        address = self.find_record_by_id(record_id)
        
        if address is None:
            return None
        
        # Read encrypted password field only
        enc_password = self.read(
            address + self.OFFSET_ENC_PASSWORD, 
            self.SIZE_ENC_PASSWORD
        )
        
        return enc_password
    
    def write_encrypted_password(self, record_id, encrypted_password):
        address = self.find_record_by_id(record_id)
        
        if address is None:
            print("Record not found")
            return False
        
        if len(encrypted_password) != self.SIZE_ENC_PASSWORD:
            raise ValueError("Encrypted password must be 16 bytes")
        
        # Read entire record
        record = self.read(address, self.RECORD_SIZE)
        
        # Get sector info
        sector_start = (address // self.SECTOR_SIZE) * self.SECTOR_SIZE
        
        # Erase sector (required before write)
        if not self.erase_sector(address):
            return False
        
        # Update password in record
        record_list = bytearray(record)
        record_list[self.OFFSET_ENC_PASSWORD:self.OFFSET_ENC_PASSWORD + self.SIZE_ENC_PASSWORD] = encrypted_password
        
        # Write back
        return self.write(address, bytes(record_list))
    
    def dump_records(self, max_records=10):
        print("\nFlash Record Dump")
        count = 0
        
        for slot in range(min(max_records, self.MAX_RECORDS)):
            address = self.get_record_address(slot)
            record_id = self.read(address, self.SIZE_ID)
            
            # Skip empty slots
            if record_id == b'\xFF\xFF\xFF\xFF':
                continue
            
            # Skip deleted slots
            if record_id == b'\x00\x00\x00\x00':
                print(f"Slot {slot:3d}: DELETED")
                continue
            
            record = self.read_record(address)
            
            print(f"Slot {slot:3d} (0x{address:06X}):")
            print(f"ID: {record['id']}")
            print(f"Enc PWD: {record['encrypted_password'].hex()}")
            print(f"Enc PIN: {record['encrypted_pin'].hex()}")
            print(f"MAC: {record['mac'].hex()}")
            
            count += 1
        
        print(f"\nTotal records: {count}")
        print("=" * 40)