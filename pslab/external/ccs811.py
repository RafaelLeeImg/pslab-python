import time
from numpy import int16
from pslab.bus import I2CSlave


global debug


def debug_print(value):
    if debug == True:
        print(value)


class CCS811(I2CSlave):
    MODE_IDLE = 0  # Idle (Measurements are disabled in this mode)
    MODE_CONTINUOUS = 1  # Constant power mode, IAQ measurement every 1s
    MODE_PULSE = 2  # Pulse heating mode IAQ measurement every 10 seconds
    MODE_LOW_POWER = 3  # Low power pulse heating mode IAQ measurement every 60 seconds
    MODE_CONTINUOUS_FAST = 4  # Constant power mode, sensor measurement every 250ms

    _ADDRESS = 0x5A

    # Figure 14: CCS811 Application Register Map
    _STATUS = 0x00  # STATUS # R 1 byte Status register
    # MEAS_MODE # R/W 1 byte Measurement mode and conditions register Algorithm result. The most significant 2 bytes contain a up to ppm estimate of the equivalent CO2 (eCO2) level, and
    _MEAS_MODE = 0x01
    _ALG_RESULT_DATA = 0x02  # ALG_RESULT_DATA # R 8 bytes the next two bytes contain a ppb estimate of the total VOC level. Raw ADC data values for resistance and current source
    _RAW_DATA = 0x03  # RAW_DATA # R 2 bytes used. Temperature and humidity data can be written to
    _ENV_DATA = 0x05  # ENV_DATA # W 4 bytes enable compensation Thresholds for operation when interrupts are only
    _THRESHOLDS = 0x10  # THRESHOLDS # W 4 bytes generated when eCO2 ppm crosses a threshold The encoded current baseline value can be read. A
    # BASELINE # R/W 2 bytes previously saved encoded baseline can be written.
    _BASELINE = 0x11
    _HW_ID = 0x20  # HW_ID # R 1 byte Hardware ID. The value is 0x81
    _HW = 0x21  # HW Version # R 1 byte Hardware Version. The value is 0x1X Firmware Boot Version. The first 2 bytes contain the
    _FW_Boot_Version = 0x23  # FW_Boot_Version # R 2 bytes firmware version number for the boot code. Firmware Application Version. The first 2 bytes contain
    # FW_App_Version # R 2 bytes the firmware version number for the application code
    _FW_App_Version = 0x24
    # Internal_State # R 1 byte Internal Status register Error ID. When the status register reports an error its
    _Internal_State = 0xA0
    # ERROR_ID # R 1 byte source is located in this register If the correct 4 bytes ( 0x11 0xE5 0x72 0x8A) are written
    _ERROR_ID = 0xE0
    # SW_RESET # W 4 bytes to this register in a single sequence the device will reset and return to BOOT mode.
    _SW_RESET = 0xFF

    # Figure 25: CCS811 Bootloader Register Map
    # Address Register R/W Size Description
    _STATUS = 0x00
    _HW_ID = 0x20
    _HW_Version = 0x21
    _APP_ERASE = 0xF1
    _APP_DATA = 0xF2
    _APP_VERIFY = 0xF3
    _APP_START = 0xF4
    _SW_RESET = 0xFF

    def __init__(self, **args):
        print("ccs811 __init__()")
        # self.I2C = I2C
        self._ADDRESS = args.get('address', self._ADDRESS)
        # self.address = self._ADDRESS
        super().__init__(self._ADDRESS)
        self.fetchID()
        self.softwareReset()

    def softwareReset(self):
        print("software reset")
        self.write([0x11, 0xe5, 0x72, 0x8a], self._SW_RESET)

        # time.sleep(0.01)  # 10ms
        # self.read(100, 0)  # read 100 bytes, from register 0 clear the bus maybe?
        # self.write(self._HW_ID)

    def fetchID(self):
        hardware_id = (self.read(1, self._HW_ID))[0]
        print(f'hex(hardware_id) = {hex(hardware_id)}')
        time.sleep(0.02)  # 20ms
        hardware_version = (self.read(1, self._HW_Version))[0]
        print(f'hex(hardware_version) = {hex(hardware_version)}')
        time.sleep(0.02)  # 20ms
        boot_version = (self.read(2, self._FW_Boot_Version))[0]
        print(f'hex(boot_version) = {hex(boot_version)}')
        time.sleep(0.02)  # 20ms
        app_version = (self.read(2, self._FW_App_Version))[0]
        print(f'hex(app_version) = {hex(app_version)}')

    def appErase(self):
        ignore = self.write([0xE7, 0xA7, 0xE6, 0x09], self._APP_ERASE)
        time.sleep(0.3)

    def appStart(self):
        # write to _APP_Start and read 9 bytes, ignore the result
        # ignore = self.read(10, self._APP_START)
        ignore = self.write([], self._APP_START)
        print("after APP_START\n")

    def setMeasureMode(self, mode):
        print(f'mode = {mode}')
        print(f'register = {self._MEAS_MODE}')
        self.write([mode << 4], self._MEAS_MODE)

    def getMeasureMode(self):
        print(self.read(10, self._MEAS_MODE))

    def getStatus(self):
        status = (self.read(1, self._STATUS))[0]
        print(f'status = {bin(int(status))}')
        return status

    def decodeStatus(self, status):
        # Bit(s) Field
        BIT_FW_MODE = 7
        BIT_APP_ERASE = 6
        BIT_APP_VERIFY = 5
        BIT_APP_VALID = 4
        BIT_DATA_READY = 3
        # 2:1 -
        BIT_ERROR = 0

        if (status & (1 << BIT_FW_MODE)) > 0:
            print("Sensor is in application mode")
        else:
            print("Sensor is in boot mode")
        if (status & (1 << BIT_APP_ERASE)) > 0:
            print("APP_ERASE")
        if (status & (1 << BIT_APP_VERIFY)) > 0:
            print("APP_VERIFY")
        if (status & (1 << BIT_APP_VALID)) > 0:
            print("APP_VALID")
        if (status & (1 << BIT_DATA_READY)) > 0:
            print("DATA_READY")
        if (status & (1 << BIT_ERROR)) > 0:
            print("ERROR")

    def measure(self):
        data = self.read(8, self._ALG_RESULT_DATA)
        eCO2 = data[0] * 256 + data[1]
        eTVOC = data[2] * 256 + data[3]
        status = data[4]
        error_id = data[5]
        raw_data = 256 * data[6] + data[7]
        raw_current = raw_data >> 10
        raw_voltage = (raw_data & ((1 << 10) - 1)) * (1.65 / 1023)

        print(f'eCO2 = {eCO2}, eTVOC = {eTVOC}, status = {status}, error_id = {error_id}')
        print(f'current = {raw_current}, voltage = {raw_voltage}')
        if error_id == 0:
            # print("no_error")
            pass
        elif error_id == 1:
            print("The CCS811 received an I²C read request to a mailbox ID that is invalid")
        else:
            print("Other error")


def connect(route, **args):
    return TSL2561(route, **args)
