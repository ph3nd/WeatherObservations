#!/usr/bin/env python

from observation import WeatherObservation
from TSL2561 import LuxMeter
from BMP280 import BMP280
from SI7021 import SI7021
import requests
import csv

class Observe:
    def __init__(self):
        self._luxMeter = LuxMeter()
        self._lux = 0
        self._ambient = 0
        self._ifraRed = 0

        self._presMeter = BMP280()
        self._pressure = 0
        self._tempPres = 0

        self._humMeter = SI7021()
        self._humidity = 0
        self._tempHum = 0

    def GetObservations(self):
        self._lux, self._ambient, self._infraRed = self._luxMeter.readVisibleLux()
        
        self._pressure = self._presMeter.GetPressure()
        self._tempPres = self._presMeter.GetTemperature()

        self._humidity = self._humMeter.GetRHumidity()
        self._tempHum = self._humMeter.GetTemperature()

    def WriteCSV(self):
        pass

    def PostObservations(self):
        pass


def sense():
    obs = Observe()

    obs.GetObservations()

    print "Lux: {}, Ambient {}, Infra Red {}".format(obs._lux, obs._ambient, obs._infraRed)
    print "Pressure {}, Temperature {}".format(obs._pressure, obs._tempPres)
    print "Relative Humidity {}, Temperature {}".format(obs._humidity, obs._tempHum)


if __name__ == "__main__":
    sense() 
