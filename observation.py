#!/usr/bin/env python

import json


# Defined ranges that observations can fall into, If an
# observation falls outside of this range it will be set to 0
MIN_TEMPERATURE = -10
MAX_TEMPERATURE = 85

MIN_PRESSURE = 85000
MAX_PRESSURE = 108000

MIN_HUMIDITY = 0
MAX_HUMIDITY = 100

MIN_LUX = 0
MAX_LUX = 40000

MIN_ALTITUDE = 0
MAX_ALTITUDE = 10000

class WeatherObservation:
    """
        Represents a weather object with Temperature, Barametric Pressure,
        Relative Humidity, Lux, Altitude.

        Takes data in the form of
        dict {
            temp: 0,
            pres: 0,
            rhum: 0,
            lux: [{
                lux: 0,
                ambient: 0,
                InfraRed: 0
            }],
            alt: 0,
            time: 0,
            raw: {}
        }
    """

    # Valid weather types
    OBSERVATION_TYPE = ["temp", "pres", "rhum", "lux", "alt", "time", "raw"]

    def __init__(self, _obs):
        self._observation = dict()

        for key in self.OBSERVATION_TYPE:
            self._observation[key] = 0

        self.setObservation(_obs)

    def getObservation(self):
        return self._observation

    def setObservation(self, _obs):
        # TODO: Add bounds checking for each observation_type

        if type(_obs) == tuple:
            _dict = dict()
            _dict["temp"] = _obs[0]
            _dict["pres"] = _obs[1]
            _dict["rhum"] = _obs[2]
            _dict["lux"] = {
                "lux": _obs[3],
                "ambient": _obs[4],
                "infrared": _obs[5]
            }
            _dict["alt"] = _obs[6]
            _dict["time"] = _obs[7]
            _dict["raw"] = _obs
            _obs = _dict

        if type(_obs) == dict:
            for key, value in _obs.iteritems():
                if( key in self.OBSERVATION_TYPE ):
                    # Check all values fall within our bounds and truncate
                    # to sensible decimal places
                    if key == "temp":
                        if value < MIN_TEMPERATURE:
                            value = MIN_TEMPERATURE
                        elif value > MAX_TEMPERATURE:
                            value = MAX_TEMPERATURE
                    elif key == "pres":
                        if value < MIN_PRESSURE:
                            value = MIN_PRESSURE
                        elif value > MAX_PRESSURE:
                            value = MAX_PRESSURE
                    elif key == "rhum":
                        if value < MIN_HUMIDITY:
                            value = MIN_HUMIDITY
                        elif value > MAX_HUMIDITY:
                            value = MAX_HUMIDITY
                    elif key == "lux":
                        if value["luxd"] < MIN_LUX:
                            value["luxd"] = MIN_LUX
                        elif value["luxd"] > MAX_LUX:
                            value["luxd"] = MAX_LUX
                    elif key == "alt":
                        if value < MIN_ALTITUDE:
                            value = MIN_ALTITUDE
                        elif value > MAX_ALTITUDE:
                            value = MAX_ALTITUDE

                    self._observation[key] = value
                else:
                    print "unused key: " + key
        else:
            return "Unknown format"    
