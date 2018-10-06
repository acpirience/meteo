"""
    give the current weather and forecast for 5 days for a list of cities from openweathermap.org
"""

import json
import logging
from datetime import datetime
import requests
from dateutil.parser import parse
import pytz
from tzlocal import get_localzone

API_URLS = {
    "CURRENT": "https://api.openweathermap.org/data/2.5/weather?id=",
    "FORECAST": "https://api.openweathermap.org/data/2.5/forecast?id=",
}

CACHE_FILENAME = "meteopy"
CACHE_EXTENSION = ".cache"


class CityMeteo:
    """ main class for module meteopy """

    def __init__(self, api_key, city):
        self.key = api_key
        self.city = str(city)
        self.use_cache = False
        self.city_name = ""
        self.load_cache()
        self.current_weather = self.get_current_weather()
        self.forecast_weather = self.get_forecast_weather()
        self.update_cache()

    @property
    def cache_name(self):
        """ Returns the cache filename """
        return f"{CACHE_FILENAME}{self.city}.{CACHE_EXTENSION}"

    def call_weather_api(self, weather_type):
        """Calls the openweathermap API and returns a json dict"""
        return requests.get(
            f"{API_URLS[weather_type]}{self.city}&APPID={self.key}"
        ).json()

    @staticmethod
    def kelvin_to_celcius(temp):
        """Transform Kelvin temperature to Celcius"""
        return round(temp - 273.15, 1)

    @staticmethod
    def utc_time_to_local_time(utc_time, local_zone=None):
        """Transform UTC datemine to local timezone (or the one provided if any)"""
        utc_date = datetime.utcfromtimestamp(utc_time)
        # Timezone conversion
        utc_date = pytz.UTC.localize(utc_date)
        # if no local zone was provided, get it locally
        if not local_zone:
            local_zone = get_localzone()

        pst = pytz.timezone(str(local_zone))
        return utc_date.astimezone(pst)

    def load_cache(self):
        """"check cache presence, if absent create it then load cache"""
        try:
            with open(self.cache_name, "r") as file_cache:
                cache_content = file_cache.read()
        except FileNotFoundError:
            with open(self.cache_name, "w") as file_cache:
                cache_content = ""

        # transform cache to json object, handle cache case
        try:
            self.cache = json.loads(cache_content)
        except ValueError:
            self.cache = {
                "last_mod": "1900-01-01 00:00:00.0",
                "current_weather": {},
                "forecast_weather": {},
            }

        # validate last modification < 1 hour
        delta = datetime.now() - parse(self.cache["last_mod"])
        delta_to_hour = (delta.days * 24) + (delta.seconds / 3600)
        self.use_cache = delta_to_hour < 1

    def get_current_weather(self):
        """ get current weather from the openweathermap API """
        current = {}

        if self.use_cache:
            logging.debug("Using cache for city Id:%s", self.city)
            api_response = self.cache["current_weather"]
        else:
            logging.debug("Calling API for city Id:%s", self.city)
            api_response = self.call_weather_api("CURRENT")

        self.city_name = api_response["name"]
        current["desc"] = api_response["weather"][0]["description"]
        current["temp"] = self.kelvin_to_celcius(api_response["main"]["temp"])
        current["pressure"] = api_response["main"]["pressure"]
        current["humidity"] = api_response["main"]["humidity"]
        current["wind_speed"] = api_response["wind"]["speed"]
        current["wind_deg"] = api_response["wind"]["deg"]
        current["sunrise"] = api_response["sys"]["sunrise"]
        current["sunset"] = api_response["sys"]["sunset"]

        # update cache in memory
        if not self.use_cache:
            self.cache["last_mod"] = str(datetime.now())
            self.cache["current_weather"] = api_response

        logging.debug(
            "Stored current weather for city %s: %s", self.city, self.city_name
        )
        return current

    def get_forecast_weather(self):
        """ get forecast weather in 5 days from the openweathermap API """
        if self.use_cache:
            api_response = self.cache["forecast_weather"]
        else:
            api_response = self.call_weather_api("FORECAST")

        forecast = {}

        for measure in api_response["list"]:
            forecast_key = self.utc_time_to_local_time(measure["dt"]).strftime(
                "%Y-%m-%d %H:%M"
            )
            tmp_val = {}
            tmp_val["desc"] = measure["weather"][0]["description"]
            tmp_val["temp"] = self.kelvin_to_celcius(measure["main"]["temp"])
            tmp_val["pressure"] = measure["main"]["pressure"]
            tmp_val["humidity"] = measure["main"]["humidity"]
            tmp_val["wind_speed"] = measure["wind"]["speed"]
            tmp_val["wind_deg"] = measure["wind"]["deg"]
            forecast[forecast_key] = tmp_val

        # update cache in memory
        if not self.use_cache:
            cur_date = str(datetime.now())
            self.cache["last_mod"] = cur_date
            self.cache["forecast_weather"] = api_response

        logging.debug(
            "Stored forecast weather for next 5 days: %s values", len(forecast)
        )
        return forecast

    def update_cache(self):
        """ update the cache file on disk """
        if not self.use_cache:
            with open(self.cache_name, "w") as file_cache:
                json.dump(self.cache, file_cache)


if __name__ == "__main__":
    pass
