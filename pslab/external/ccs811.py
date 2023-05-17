import time
from numpy import int16
from pslab.bus import I2CSlave


global debug


def debug_print(value):
    if debug == True:
        print(value)


class CCS811(I2CSlave):
    _MODE_IDLE = 0  # Idle (Measurements are disabled in this mode)
    _MODE_CONTINUOUS = 1  # Constant power mode, IAQ measurement every 1s
    _MODE_PULSE = 2  # Pulse heating mode IAQ measurement every 10 seconds
    _MODE_LOW_POWER = 3  # Low power pulse heating mode IAQ measurement every 60 seconds
    _MODE_CONTINUOUS_QUARTER = 4  # Constant power mode, sensor measurement every 250ms

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
    _FW_Boot_Version = 0x23
    _FW_App_Version = 0x24
    _ERROR_ID = 0xE0
    _APP_ERASE = 0xF1
    _APP_DATA = 0xF2
    _APP_VERIFY = 0xF3
    _APP_START = 0xF4
    _SW_RESET = 0xFF

    def __init__(self, **args):
        self.softwareReset()

    def softwareReset(self):
        self._ADDRESS = args.get('address', self._ADDRESS)
        super().__init__(self._ADDRESS)
        self.I2C.writeBulk(self.ADDRESS, [0xff, 0x11, 0xe5, 0x72, 0x8a])
        time.sleep(0.01)  # 10ms
        self.I2C.readBulk(0, 100)  # read 100 bytes, clear the bus maybe?
        # self.write(self._HW_ID)
        hw_id = self.read(self._HW_ID)
        time.sleep(0.02)  # 20ms

    def appStart(self):
        # write to _APP_Start and read 9 bytes, ignore the result
        ignore = self.read(self._APP_START)
        self.I2C.readBulk(0, 9)
        (display "after APP_START\n"))

    def setMeasureMode(self):
        CCS811_REG_MEAS_MODE
        pass

    def getMeasureMode(self):
        pass

    def getMeasureMode(self):
        pass

    def measure(self):
        pass



def connect(route, **args):
    return TSL2561(route, **args)
