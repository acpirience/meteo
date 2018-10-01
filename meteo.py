import requests
import yaml
import logging
from datetime import datetime
from dateutil import tz


def call_api(url, city, api_key):
    request_url = f"{url}{config['villes'][city]}&APPID={api_key}"
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


# logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")

file_handler = logging.FileHandler("meteo.log")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console)

# Read API key from file
with open("openweathermap.api", "r") as key:
    api_key = key.read()

# Load yaml config
with open("config.yml", "r") as yml_file:
    config = yaml.load(yml_file)

# get weather for each cities
for city in config["villes"]:
    # current weather
    api_response = call_api(config["api"]["current_weather"], city, api_key)

    desc = api_response["weather"][0]["description"]
    temp, pressure, humidity, wind_speed, wind_deg = (
        api_response["main"]["temp"],
        api_response["main"]["pressure"],
        api_response["main"]["humidity"],
        api_response["wind"]["speed"],
        api_response["wind"]["deg"],
    )
    sunrise, sunset = api_response["sys"]["sunrise"], api_response["sys"]["sunset"]

    # logger.info(f"Current weather in {city}: {desc}")
    logger.info(f"  Current Temperature: {kelvin_to_celcius(temp)}C")
    logger.info(
        f"  Wind: {wind_speed} m/s ({wind_deg} deg), Pressure: {pressure} hPa, Humidity: {humidity}%"
    )
    logger.info(
        f"  Sunrise: {unix_to_local_time(sunrise).strftime('%H:%M:%S')} - Sunset: {unix_to_local_time(sunset).strftime('%H:%M:%S')}"
    )
    logger.info("-" * 80)

    # forecast weather in 5 days
    api_response = call_api(config["api"]["forecast_weather"], city, api_key)
    forecast = dict()

    for measure in api_response["list"]:
        forecast_key = unix_to_local_time(measure["dt"]).strftime("%Y-%m-%d %H:%M:%S")
        tmp_val = dict()
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

    logger.info(f"Forecast for next 5 days:")
    for key in forecast:
        log = " ".join(
            (
                f"{key} : ",
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
