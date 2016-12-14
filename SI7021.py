# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# SI7021
# This code is designed to work with the SI7021_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Humidity?sku=SI7021_I2CS#tabs-0-product_tabset-2

import Adafruit_GPIO.I2C as I2C
import time

RH_NOHOLD_MASTER = 0xF5
T_NOHOLD_MASTER = 0xF3

class SI7021:

    def __init__(self, address=0x40):
        self.address = 0x40
        self._i2c = I2C.get_i2c_device(address)

    def GetRHumidity(self):
        # Set the device mode for humidity
        self._i2c.writeRaw8(RH_NOHOLD_MASTER)
        time.sleep(0.3)

        # Read 2 bytes from the sensor
        msb = self._i2c.readRaw8()
        lsb = self._i2c.readRaw8()
        checksum = self._i2c.readRaw8()

        rawVal = (msb << 8) | lsb

        self._rHumidity = (rawVal  * 125 / 65536.0) - 6
        return self._rHumidity

    def GetTemperature(self):
        # Set the device mode for temperature
        self._i2c.writeRaw8(T_NOHOLD_MASTER)
        time.sleep(0.3)
        
        msb = self._i2c.readRaw8()
        lsb = self._i2c.readRaw8()

        rawVal = (msb << 8) | lsb

        self._temperature = (rawVal  * 175.72 / 65536.0) - 46.85
        return self._temperature
