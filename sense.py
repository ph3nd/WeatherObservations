#!/usr/bin/env python

from observation import WeatherObservation
from TSL2561 import LuxMeter
from BMP280 import BMP280
from SI7021 import SI7021
import requests
import csv
import time
import json

class Observe:
    def __init__(self):
        self._luxMeter = LuxMeter()
        self._presMeter = BMP280()
        self._humMeter = SI7021()

        self._observation = None

    def GetObservations(self):
        obs = dict()
        lux = 0
        ambient = 0
        infraRed = 0

        timestamp = int(time.time())
        lux, ambient, infraRed = self._luxMeter.readVisibleLux()

        pressure = self._presMeter.GetPressure()
        tempPres = self._presMeter.GetTemperature()
        altitude = self._presMeter.GetAltitude()

        humidity = self._humMeter.GetRHumidity()
        tempHum = self._humMeter.GetTemperature()

        obs["temp"] = tempHum
        obs["pres"] = pressure
        obs["rhum"] = humidity
        
        luxd = dict()
        luxd["luxd"] = lux
        luxd["ambient"] = ambient
        luxd["infrared"] = infraRed

        obs["lux"] = {}
        obs["lux"] = luxd
        obs["alt"] = altitude
        obs["time"] = timestamp
        obs["raw"] = dict(obs)
        obs["raw"]["temp2"] = tempPres

        self._observation = WeatherObservation(obs)
        return self._observation.getObservation()

    def WriteCSV(self):
        pass

    def PostObservations(self):
        r = requests.post('http://localhost:80/api/addobservation', data=json.dumps(self._observation.getObservation()), headers={'Content-type':'application/json',})

def sense():
    obs = Observe()
    x = obs.GetObservations()
    obs.PostObservations()

if __name__ == "__main__":
    while True:
        sense()
        time.sleep(30)
