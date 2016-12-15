#!/usr/bin/env python

import sys
import smbus
import time
import datetime
import Adafruit_GPIO.I2C as I2C

# ===========================================================================
# Program to log the output of two TLS2561 Luxmeters on the same extended i2c bus.
# i2c bus is 4-way 20 AWG ribbon cable with SDA and SCL on the outside cores. 
# Each sensor is 4.5 metres from the RPi.  i2c bus has its own 3v3 power supply.
#
# Automatically switches from high gain to low gain as brightness increases.
# 
# Uses lots of ideas from Adafruit code, and their I2C & gspread libraries
#
# Google Account Details
# ===========================================================================

####################################
# address param for Luxmeter instance is set by ADDR pin connection: 
#  0x29 = ADDR tied to 0v
#  0x49 = ADDR tied to 3v3
#  0x39 = ADDR left floating (default, but not used here)
#
# Param is gain and integration timing - only 0x01 and 0x11 are used here
#  0x00 = no gain, 13 mSec  (brightest)
#  0x01 = no gain, 101 mSec
#  0x02 = no gain, 402 mSec
#  0x10 = 16X gain, 13 mSec
#  0x11 = 16X gain, 101 mSec
#  0x12 = 16X gain, 402 mSec (darkest)
#######################################
#

class Luxmeter :
  i2c = None

  def __init__(self, address=0x39, debug=0):
    self.i2c = I2C.get_i2c_device(address)
    self.address = address
    self.debug = debug

    self.i2c.write8(0x80, 0x03)     # enable the device
    self.i2c.write8(0x81, 0x11)     # set gain = 16X and timing = 101 mSec

  def readfull(self, reg=0x8C):
    "Reads visible + IR value from the I2C device"
    try:
      fullval = self.i2c.readU16(reg)
      newval = I2C.reverseByteOrder(fullval)
      if (self.debug):
        print "I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, fullval & 0xFFFF, reg)
      return newval
    except IOError, err:
      print "Error accessing 0x%02X: Check your I2C address" % self.address
      return -1

  def readIR(self, reg=0x8E):
    "Reads IR value from the I2C device"
    try:
      IRval = self.i2c.readU16(reg)
      newIR = I2C.reverseByteOrder(IRval)
      if (self.debug):
        print "I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, IRval & 0xFFFF, reg)
      return newIR
    except IOError, err:
      print "Error accessing 0x%02X: Check your I2C address" % self.address
      return -1

# Continuously append data from East- and West-facing sensors
while(True):
  eastlux = Luxmeter(0x39, False)       # create instance with 0v i2c address and no debug messages
  eastlux.i2c.write8(0x80, 0x03)     # enable the device
  eastlux.i2c.write8(0x81, 0x11)     # set gain = 16X and timing = 101 mSec

  egainsetting = "High gain"
  eambient = eastlux.readfull()
  if eambient >= 37177:         # sensor is maxed out, so remove the 16X gain
    eastlux.i2c.write8(0x81,0x01)
    egainsetting = "Low gain"
    time.sleep(0.41)
    eambient = eastlux.readfull()   # try again

  time.sleep(0.41)         # allow for slowest A2D conversion
  einfra = eastlux.readIR()
  time.sleep(0.41)         # allow for slowest A2D conversion

# the RPi has floating point, so these calculations are MUCH easier than they are
# for an Arduino! - taken from TAOS datasheet

  ratio = (float) (einfra / eambient)

  if ((ratio >= 0) & (ratio <= 0.52)):
   elux = (0.0315 * eambient) - (0.0593 * eambient * (ratio**1.4))
  elif (ratio <= 0.65):
   elux = (0.0229 * eambient) - (0.0291 * einfra)
  elif (ratio <= 0.80):
    elux = (0.0157 * eambient) - (0.018 + einfra)
  elif (ratio <= 1.3):
    elux = (0.00338 * eambient) - (0.0026 * einfra)
  elif (ratio > 1.3):
        elux = 0

  print "egainsetting: {}, ambient: {}, infra: {}, lux: {}".format(egainsetting, eambient, einfra, elux) 
  time.sleep(1)

