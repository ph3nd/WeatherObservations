#!/usr/bin/python

import sys
import smbus
import time
import datetime
import gspread
from Adafruit_I2C import Adafruit_I2C

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

# Account details for google docs
email       = 'some.user@gmail.com'
password    = 'somesecret'
spreadsheet = 'Rooftop_Lux'

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
# Login with your Google account
try:
  gc = gspread.login(email, password)
except:
  print "Unable to log in.  Check your email address/password"
  sys.exit()

# Open a worksheet from your spreadsheet using the filename
try:
  worksheet = gc.open(spreadsheet).sheet1
  # Alternatively, open a spreadsheet using the spreadsheet's key
  # worksheet = gc.open_by_key('0ApwDUb5fnx_XdENOV1Rncmpac25jMkd3d1lEM1RKUnc')
except:
  print "Unable to open the spreadsheet.  Check your filename: %s" % spreadsheet
  sys.exit()

class Luxmeter :
  i2c = None

  def __init__(self, address=0x39, debug=0):
    self.i2c = Adafruit_I2C(address)
    self.address = address
    self.debug = debug

    self.i2c.write8(0x80, 0x03)     # enable the device
    self.i2c.write8(0x81, 0x11)     # set gain = 16X and timing = 101 mSec

  def readfull(self, reg=0x8C):
    "Reads visible + IR value from the I2C device"
    try:
      fullval = self.i2c.readU16(reg)
      newval = self.i2c.reverseByteOrder(fullval)
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
      newIR = self.i2c.reverseByteOrder(IRval)
      if (self.debug):
        print "I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, IRval & 0xFFFF, reg)
      return newIR
    except IOError, err:
      print "Error accessing 0x%02X: Check your I2C address" % self.address
      return -1

# Continuously append data from East- and West-facing sensors
while(True):
  eastlux = Luxmeter(0x29,False)       # create instance with 0v i2c address and no debug messages
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

  westlux = Luxmeter(0x49,False)      # create instance with 3v3 i2c address and no debug messages
  westlux.i2c.write8(0x80, 0x03)     # enable the device
  westlux.i2c.write8(0x81, 0x11)     # set gain = 16X and timing = 101 mSec

  wgainsetting = "High gain"
  wambient = westlux.readfull()
  if wambient >= 37177:         # sensor is maxed out, so remove the 16X gain
    westlux.i2c.write8(0x81,0x01)
    wgainsetting = "Low gain"
    time.sleep(0.41)
    wambient = westlux.readfull()    # try again

#  wambient = wambient + fudgefactor   # add offset to match up the two sensors

  time.sleep(0.41)         # allow for slowest A2D conversion
  winfra = westlux.readIR()
  time.sleep(0.41)         # allow for slowest A2D conversion

  ratio = (float) (winfra / wambient)

  if ((ratio >= 0) & (ratio <= 0.52)):
   wlux = (0.0315 * wambient) - (0.0593 * wambient * (ratio**1.4))
  elif (ratio <= 0.65):
   wlux = (0.0229 * wambient) - (0.0291 * winfra)
  elif (ratio <= 0.80):
    wlux = (0.0157 * wambient) - (0.018 + winfra)
  elif (ratio <= 1.3):
    wlux = (0.00338 * wambient) - (0.0026 * winfra)
  elif (ratio > 1.3):
        wlux = 0

  if (elux + wlux) > 10:      # don't log in the dark!
    # Append the data to the spreadsheet, including a timestamp
    try:
      values = [datetime.datetime.now(), egainsetting, eambient, einfra, elux, wgainsetting, wambient, winfra, wlux]
      worksheet.append_row(values)
    except:
      print "Unable to append data.  Check your connection?"
      sys.exit()

    print "East Lux = %.2f, West Lux = %.2f. Wrote a row to %s" % (elux, wlux, spreadsheet)

  # Get one set of readings every three minutes
  time.sleep(173)
