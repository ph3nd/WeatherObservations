import Adafruit_GPIO.I2C as I2C
import time
from lxml import html
import requests

# power mode
# POWER_MODE=0 # sleep mode
# POWER_MODE=1 # forced mode
# POWER_MODE=2 # forced mode
POWER_MODE=3 # normal mode

# temperature resolution
# OSRS_T = 0 # skipped
# OSRS_T = 1 # 16 Bit
OSRS_T = 2 # 17 Bit
# OSRS_T = 3 # 18 Bit
# OSRS_T = 4 # 19 Bit
# OSRS_T = 5 # 20 Bit

# pressure resolution
# OSRS_P = 0 # pressure measurement skipped
# OSRS_P = 1 # 16 Bit ultra low power
# OSRS_P = 2 # 17 Bit low power
# OSRS_P = 3 # 18 Bit standard resolution
# OSRS_P = 4 # 19 Bit high resolution
OSRS_P = 5 # 20 Bit ultra high resolution

# filter settings
# FILTER = 0 #
# FILTER = 1 #
# FILTER = 2 #
# FILTER = 3 #
FILTER = 4 #
# FILTER = 5 #
# FILTER = 6 #
# FILTER = 7 #

# standby settings
# T_SB = 0 # 000 0,5ms
# T_SB = 1 # 001 62.5 ms
# T_SB = 2 # 010 125 ms
# T_SB = 3 # 011 250ms
T_SB = 4 # 100 500ms
# T_SB = 5 # 101 1000ms
# T_SB = 6 # 110 2000ms
# T_SB = 7 # 111 4000ms

BMP280_REGISTER_DIG_T1 = 0x88
BMP280_REGISTER_DIG_T2 = 0x8A
BMP280_REGISTER_DIG_T3 = 0x8C
BMP280_REGISTER_DIG_P1 = 0x8E
BMP280_REGISTER_DIG_P2 = 0x90
BMP280_REGISTER_DIG_P3 = 0x92
BMP280_REGISTER_DIG_P4 = 0x94
BMP280_REGISTER_DIG_P5 = 0x96
BMP280_REGISTER_DIG_P6 = 0x98
BMP280_REGISTER_DIG_P7 = 0x9A
BMP280_REGISTER_DIG_P8 = 0x9C
BMP280_REGISTER_DIG_P9 = 0x9E
BMP280_REGISTER_CHIPID = 0xD0
BMP280_REGISTER_VERSION = 0xD1
BMP280_REGISTER_SOFTRESET = 0xE0
BMP280_REGISTER_CONTROL = 0xF4
BMP280_REGISTER_CONFIG  = 0xF5
BMP280_REGISTER_STATUS = 0xF3
BMP280_REGISTER_TEMPDATA_MSB = 0xFA
BMP280_REGISTER_TEMPDATA_LSB = 0xFB
BMP280_REGISTER_TEMPDATA_XLSB = 0xFC
BMP280_REGISTER_PRESSDATA_MSB = 0xF7
BMP280_REGISTER_PRESSDATA_LSB = 0xF8
BMP280_REGISTER_PRESSDATA_XLSB = 0xF9

class BMP280:
    def __init__(self, i2caddr=0x77):
        self._i2c = I2C
        self._device=i2c.get_i2c_device(i2caddr)

        self._config = (T_SB <<5) + (FILTER <<2)
        self._ctrlmeas = (OSRS_T <<5) + (OSRS_P <<2) + POWER_MODE

        #self._QNH = self._GetQNH()

        err, errmsg = self._Setup()
        if err == False:
            print errmsg

    def GetTemperature(self):
        raw_temp_msb=device.readU8(BMP280_REGISTER_TEMPDATA_MSB)
        raw_temp_lsb=device.readU8(BMP280_REGISTER_TEMPDATA_LSB)
        raw_temp_xlsb=device.readU8(BMP280_REGISTER_TEMPDATA_XLSB)

        # combine 3 bytes  msb 12 bits left, lsb 4 bits left, xlsb 4 bits right
        raw_temp=(raw_temp_msb <<12)+(raw_temp_lsb<<4)+(raw_temp_xlsb>>4)

        # formula for temperature from datasheet
        var1=(raw_temp/16384.0-dig_T1/1024.0)*dig_T2
        var2=(raw_temp/131072.0-dig_T1/8192.0)*(raw_temp/131072.0-dig_T1/8192.0)*dig_T3
        self._temp=(var1+var2)/5120.0

        self._t_fine=(var1+var2) # need for pressure calculation

        return self._temp

    def GetPressure(self):
        self.GetTemperature()

        raw_press_msb=device.readU8(BMP280_REGISTER_PRESSDATA_MSB)
        raw_press_lsb=device.readU8(BMP280_REGISTER_PRESSDATA_LSB)
        raw_press_xlsb=device.readU8(BMP280_REGISTER_PRESSDATA_XLSB)

        # combine 3 bytes  msb 12 bits left, lsb 4 bits left, xlsb 4 bits right
        raw_press=(raw_press_msb <<12)+(raw_press_lsb <<4)+(raw_press_xlsb >>4)

        # formula for pressure from datasheet
        var1=self._t_fine/2.0-64000.0
        var2=var1*var1*dig_P6/32768.0
        var2=var2+var1*dig_P5*2
        var2=var2/4.0+dig_P4*65536.0
        var1=(dig_P3*var1*var1/524288.0+dig_P2*var1)/524288.0
        var1=(1.0+var1/32768.0)*dig_P1
        press=1048576.0-raw_press
        press=(press-var2/4096.0)*6250.0/var1
        var1=dig_P9*press*press/2147483648.0
        var2=press*dig_P8/32768.0

        self._press=press+(var1+var2+dig_P7)/16.0

        return self._press

    def GetAltitude(self):
        self.GetPressure()

        self._altitude = 44330.0 * (1.0 - pow(self._press / (self._QNH*100), (1.0/5.255))) # formula for altitude from airpressure

        return self._altitude
        

    def _Setup(self):
        # Check sensor id 0x58=BMP280
        if (device.readS8(BMP280_REGISTER_CHIPID) == 0x58):
            # Reset sensor
            device.write8(BMP280_REGISTER_SOFTRESET,0xB6
            time.sleep(0.2)
            device.write8(BMP280_REGISTER_CONTROL,CTRL_MEAS)
            time.sleep(0.2)
            device.write8(BMP280_REGISTER_CONFIG,CONFIG)
            time.sleep(0.2)

            # read correction settings
            self._dig_T1 = device.readU16LE(BMP280_REGISTER_DIG_T1)
            self._dig_T2 = device.readS16LE(BMP280_REGISTER_DIG_T2)
            self._dig_T3 = device.readS16LE(BMP280_REGISTER_DIG_T3)
            self._dig_P1 = device.readU16LE(BMP280_REGISTER_DIG_P1)
            self._dig_P2 = device.readS16LE(BMP280_REGISTER_DIG_P2)
            self._dig_P3 = device.readS16LE(BMP280_REGISTER_DIG_P3)
            self._dig_P4 = device.readS16LE(BMP280_REGISTER_DIG_P4)
            self._dig_P5 = device.readS16LE(BMP280_REGISTER_DIG_P5)
            self._dig_P6 = device.readS16LE(BMP280_REGISTER_DIG_P6)
            self._dig_P7 = device.readS16LE(BMP280_REGISTER_DIG_P7)
            self._dig_P8 = device.readS16LE(BMP280_REGISTER_DIG_P8)
            self._dig_P9 = device.readS16LE(BMP280_REGISTER_DIG_P9)
        else:
            return False, "Device not BMP280"

    def _GetQNH(area='Area 60:', url='http://www.bom.gov.au/aviation/forecasts/area-qnh/'):
        # TODO: UPDATE TO USE THE BOM API
        '''
            Gets the QNH value for provided area from provided URL
            xpath works for current bom.gov.au QNH forcast.
            Needs to be updated every 3 hours
        '''
        r = requests.get(url)
        tree = html.fromstring(r.content)

        dt = tree.xpath('//dt[contains(text(), "' + area + '")]')[0]

        dd = dt.getnext()
        qnh = dd.text
        return qnh
