#!/usr/bin/env python

import sys
import time
import Adafruit_GPIO.I2C as I2C

class Luxmeter:
    i2c = None

    def __init__(self, address=0x39, debug=0, pause=0.41):
        self._i2c = I2C.get_i2c_device(address)
        self.address = address
        self.pause = pause
        self.debug = debug

        self._i2c.write8(0x80, 0x03)     # enable the device
        self._i2c.write8(0x81, 0x11)     # set gain = 16X and timing = 101 mSec
        time.sleep(self.pause)          # pause for a warm-up

    def _readfull(self, reg=0x8C):
        """Reads visible + IR diode from the I2C device"""
        try:
            fullval = self._i2c.readU16(reg)
            newval = I2C.reverseByteOrder(fullval)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, fullval & 0xFFFF, reg))
            return newval
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def _readIR(self, reg=0x8E):
        """Reads IR only diode from the I2C device"""
        try:
            IRval = self._i2c.readU16(reg)
            newIR = I2C.reverseByteOrder(IRval)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, IRval & 0xFFFF, reg))
            return newIR
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def _readfullauto(self, reg=0x8c):
        """Reads visible + IR diode from the I2C device with auto ranging"""
        try:
            fullval = self._i2c.readU16(reg)
            newval = I2C.reverseByteOrder(fullval)
            if newval >= 37177:
                self._i2c.write8(0x81, 0x01)
                time.sleep(self.pause)
                fullval = self._i2c.readU16(reg)
                newval = I2C.reverseByteOrder(fullval)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, fullval & 0xFFFF, reg))
            return newval
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def _readIRauto(self, reg=0x8e):
        """Reads IR diode from the I2C device with auto ranging"""
        try:
            IRval = self._i2c.readU16(reg)
            newIR = I2C.reverseByteOrder(IRval)
            if newIR >= 37177:
                self._i2c.write8(0x81, 0x01)     #   remove 16x gain
                time.sleep(self.pause)
                IRval = self._i2c.readU16(reg)
                newIR = I2C.reverseByteOrder(IRval)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, IRval & 0xFFFF, reg))
            return newIR
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def LuxRead(self, autorange = True):
        """Grabs a lux reading either with autoranging or without"""
        if autorange == True:
            ambient = self._readfullauto()
            IR = self._readIRauto()
        else:
            ambient = self._readfull()
            IR = self._readIR()
            
        ratio = (float) (IR / ambient)

        if ((ratio >= 0) & (ratio <= 0.52)):
            lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio**1.4))
        elif (ratio <= 0.65):
            lux = (0.0229 * ambient) - (0.0291 * IR)
        elif (ratio <= 0.80):
            lux = (0.0157 * ambient) - (0.018 + IR)
        elif (ratio <= 1.3):
            lux = (0.00338 * ambient) - (0.0026 * IR)
        elif (ratio > 1.3):
            lux = 0
        
        self._ambient = ambient
        self._IR = IR
        self._lux = lux
        return (lux, ambient, IR)
