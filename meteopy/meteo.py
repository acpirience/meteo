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

CACHE_FILENAME = "meteopy.cache"


class meteo:
    """ main class for module meteopy """

    def __init__(self, api_key, city_list):
        self.key = api_key
        self.cities = city_list

    def call_weather_api(self, weather_type, city):
        """Calls the openweathermap API and returns a json dict"""
        return requests.get(f"{API_URLS[weather_type]}{city}&APPID={self.key}").json()

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

    def run(self):
        # check cache presence, if absent create it
        # then load cache
        try:
            with open(CACHE_FILENAME, "r") as file_cache:
                cache_content = file_cache.read()
        except FileNotFoundError:
            with open(CACHE_FILENAME, "w") as file_cache:
                cache_content = ""

        # transform cache to json object, handle cache case
        try:
            cache = json.loads(cache_content)
        except ValueError:
            cache = {}

        # get weather for each cities
        for city in self.cities:
            use_cache = False
            city = str(city)  # Dict keys are only string ...

            # check if we can use cache
            if city not in cache:
                cache[city] = {
                    "last_mod": "1900-01-01 00:00:00.0",
                    "current_weather": {},
                    "forecast_weather": {},
                }

            # validate last modification < 1 hour
            cur_date = datetime.now()
            last_mod = parse(cache[city]["last_mod"])
            delta = cur_date - last_mod
            delta_to_hour = (delta.days * 24) + (delta.seconds / 3600)
            if delta_to_hour < 1:
                use_cache = True

            if use_cache:
                logging.debug(f"Using cache for city Id:{city}")
            else:
                logging.debug(f"Calling API for city Id:{city}")

            # current weather
            if use_cache:
                api_response = cache[city]["current_weather"]
            else:
                api_response = self.call_weather_api("CURRENT", city)

            city_name = api_response["name"]
            desc = api_response["weather"][0]["description"]
            temp, pressure, humidity, wind_speed, wind_deg = (
                api_response["main"]["temp"],
                api_response["main"]["pressure"],
                api_response["main"]["humidity"],
                api_response["wind"]["speed"],
                api_response["wind"]["deg"],
            )
            sunrise, sunset = (
                api_response["sys"]["sunrise"],
                api_response["sys"]["sunset"],
            )

            # update cache in memory
            if not use_cache:
                cache[city]["last_mod"] = str(cur_date)
                cache[city]["current_weather"] = api_response

            logging.info(f"Current weather in {city_name}: {desc}")
            logging.info(f"  Current Temperature: {self.kelvin_to_celcius(temp)}C")

            # forecast weather in 5 days
            if use_cache:
                api_response = cache[city]["forecast_weather"]
            else:
                api_response = self.call_weather_api("FORECAST", city)

            forecast = {}

            for measure in api_response["list"]:
                forecast_key = measure["dt"]
                tmp_val = {}
                tmp_val["desc"] = measure["weather"][0]["description"]
                tmp_val["temp"], tmp_val["pressure"], tmp_val["humidity"], tmp_val[
                    "wind_speed"
                ], tmp_val["wind_deg"] = (
                    measure["main"]["temp"],
                    measure["main"]["pressure"],
                    measure["main"]["humidity"],
                    measure["wind"]["speed"],
                    measure["wind"]["deg"],
                )
                forecast[forecast_key] = tmp_val

            # update cache in memory
            if not use_cache:
                cur_date = str(datetime.now())
                cache[city]["last_mod"] = cur_date
                cache[city]["forecast_weather"] = api_response

            logging.info(f"Forecast for next 5 days: {len(forecast)} lines")
            logging.info("")

            # update cache on disk
            if not use_cache:
                with open(CACHE_FILENAME, "w") as file_cache:
                    json.dump(cache, file_cache)


def main():
    pass


if __name__ == "__main__":
    main()
