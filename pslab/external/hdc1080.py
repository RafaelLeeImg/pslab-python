import time
import struct
from pslab.bus import I2CSlave


class HDC1080(I2CSlave):
    _ADDRESS = 0x40

    # Table 1. Register Map Pointer Name Reset value Description

    # 0x00 Temperature 0x0000 Temperature measurement output
    # 0x01 Humidity 0x0000 Relative Humidity measurement output
    # 0x02 Configuration 0x1000 HDC1080 configuration and status
    # 0xFB Serial ID device dependent First 2 bytes of the serial ID of the part
    # 0xFC Serial ID device dependent Mid 2 bytes of the serial ID of the part
    # 0xFD Serial ID device dependent Last byte bit of the serial ID of the part
    # 0xFE Manufacturer ID 0x5449 ID of Texas Instruments
    # 0xFF Device ID 0x1050 ID of the device

    REG_TEMPERATURE = 0x0
    REG_HUMIDITY = 0x1
    REG_CONF = 0x2  # 2 bytes
    REG_SN_HIGH = 0xFB
    REG_SN_MIDDLE = 0xFC
    REG_SN_LOW = 0xFD
    REG_DEVICE_ID = 0xFF

    REG_CONF_RST = 15
    REG_CONF_HEAT = 13
    REG_CONF_MODE = 12
    REG_CONF_BTST = 11
    REG_CONF_TRES = 10  # 1:11 bit, 0:14 bit
    REG_CONF_HRES = 8  # 2 bits, [9:8], 00:14bit, 01:11bit, 10:8bit

    def __init__(self, **args):
        self._ADDRESS = args.get('address', self._ADDRESS)
        super().__init__(self._ADDRESS)

    def softwareReset(self):
        status_write = 0
        status_write = status_write | (1 << self.REG_CONF_RST)
        # status_write = status_write | (1 << self.REG_CONF_MODE)
        # self.write([1<<self.REG_CONF_RST],self.REG_CONF)
        # self.write([1<<self.REG_CONF_MODE],self.REG_CONF)
        # status_write = status_write.to_bytes(2, 'big')
        status_write = struct.pack(">H", status_write)
        # status_write = b'\x10\x00'
        print(f'softwareReset status = {status_write}')
        self.write(status_write, self.REG_CONF)

    def getStatus(self):
        status_read = self.read(2, self.REG_CONF)
        print("getStatus status = ", end='')
        [print(hex(i), end=', ') for i in status_read]
        print('')

    def startAcquire(self):
        status_write = 0
        status_write = status_write | (1 << self.REG_CONF_MODE)
        status_write = struct.pack(">H", status_write)
        print(f'startAcquire status = {status_write}')
        self.write(status_write, self.REG_CONF)

    def getID(self):
        serial_number = self.read(2, self.REG_SN_HIGH)
        serial_number = serial_number + self.read(2, self.REG_SN_MIDDLE)
        serial_number = serial_number + self.read(2, self.REG_SN_LOW)

        id = self.read(2, self.REG_DEVICE_ID)
        print(f'serial_number={serial_number}')
        print(f'id={id}')

    def getTemperature(self):
        self.write([], self.REG_TEMPERATURE)
        time.sleep(0.01)  # 10ms
        temperature_raw = self.read(2, self.REG_TEMPERATURE)
        temperature = temperature_raw[0] * 256 + temperature_raw[1]
        temperature = (temperature / 2**16) * 165 - 40
        print(f"temperature = {temperature}")

    def getHumidity(self):
        self.write([], self.REG_HUMIDITY)
        time.sleep(0.01)  # 10ms
        humidity_raw = self.read(2, self.REG_HUMIDITY)
        humidity = humidity_raw[0] * 256 + humidity_raw[1]
        humidity = humidity / 2**16
        print(f"humidity = {humidity}")
