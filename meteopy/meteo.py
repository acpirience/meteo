import requests
import json
import logging
from datetime import datetime
from dateutil import tz, parser
from dateutil.parser import parse


def call_api(url, city, api_key):
    request_url = f"{url}{city}&APPID={api_key}"
    return requests.get(request_url).json()


def kelvin_to_celcius(temp):
    return round(temp - 273.15, 1)


def unix_to_local_time(unix):
    # Timezone conversion
    from_zone = tz.gettz("UTC")
    to_zone = tz.gettz("CEST")

    utc = datetime.utcfromtimestamp(unix)
    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)


def run(api_key, city_list):
    # logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)

    current_weather_api_url = "https://api.openweathermap.org/data/2.5/weather?id="
    forecast_weather_api_url = "https://api.openweathermap.org/data/2.5/forecast?id="
    cache_filename = "meteopy.cache"

    # check cache presence, if absent create it
    # then load cache
    try:
        with open(cache_filename, "r") as file_cache:
            cache_content = file_cache.read()
    except FileNotFoundError:
        with open(cache_filename, "w") as file_cache:
            cache_content = ""

    # transform cache to json object, handle cache case
    try:
        cache = json.loads(cache_content)
    except:
        cache = {}

    # get weather for each cities
    for city in city_list:
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
            logger.debug(f"Using cache for city Id:{city}")
        else:
            logger.debug(f"Calling API for city Id:{city}")

        # current weather
        if use_cache:
            api_response = cache[city]["current_weather"]
        else:
            api_response = call_api(current_weather_api_url, city, api_key)

        city_name = api_response["name"]
        desc = api_response["weather"][0]["description"]
        temp, pressure, humidity, wind_speed, wind_deg = (
            api_response["main"]["temp"],
            api_response["main"]["pressure"],
            api_response["main"]["humidity"],
            api_response["wind"]["speed"],
            api_response["wind"]["deg"],
        )
        sunrise, sunset = api_response["sys"]["sunrise"], api_response["sys"]["sunset"]

        # update cache in memory
        if not use_cache:
            cache[city]["last_mod"] = str(cur_date)
            cache[city]["current_weather"] = api_response

        logger.info(f"Current weather in {city_name}: {desc}")
        logger.info(f"  Current Temperature: {kelvin_to_celcius(temp)}C")
        logger.info(
            f"  Wind: {wind_speed} m/s ({wind_deg} deg), Pressure: {pressure} hPa, Humidity: {humidity}%"
        )
        logger.info(
            f"  Sunrise: {unix_to_local_time(sunrise).strftime('%H:%M:%S')} - Sunset: {unix_to_local_time(sunset).strftime('%H:%M:%S')}"
        )
        logger.info("-" * 80)

        # forecast weather in 5 days
        if use_cache:
            api_response = cache[city]["forecast_weather"]
        else:
            api_response = call_api(forecast_weather_api_url, city, api_key)

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

        logger.info(f"Forecast for next 5 days:")
        for key in forecast:
            log = " ".join(
                (
                    f"{unix_to_local_time(key).strftime('%Y-%m-%d %H:%M:%S')} : ",
                    f"Temp.: {kelvin_to_celcius(forecast[key]['temp']):>4}C",
                    f"Wind: {forecast[key]['wind_speed']:>4} m/s",
                    f"({round(forecast[key]['wind_deg']):>3} deg),",
                    f"Pressure: {forecast[key]['pressure']:>7} hPa,",
                    f"Humidity: {forecast[key]['humidity']:>3}%",
                    f"  => {forecast[key]['desc']}",
                )
            )

            logger.info(log)
        logger.info("-" * 120)

        # update cache on disk
        if not use_cache:
            with open(cache_filename, "w") as file_cache:
                json.dump(cache, file_cache)


def main():
    pass


if __name__ == "__main__":
    main()
