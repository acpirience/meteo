import requests
import yaml
import logging
from datetime import datetime
from dateutil import tz


def make_api_url(url):
    return f"{url}{config['villes'][city]}&APPID={api_key}"

def kelvin_to_celcius(temp):
    return round(temp - 273.15, 1)

def unix_to_local_time(unix):
    # Timezone conversion
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('CEST')

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
with open("openweathermap.api","r") as key:
    api_key = key.read()

# Load yaml config
with open("config.yml","r") as yml_file:
    config = yaml.load(yml_file)

# get weather for each cites
for city in config["villes"]:
    curr_weather_url = make_api_url(config['api']["current_weather"])
    api_response = requests.get(curr_weather_url).json()

    desc = api_response['weather'][0]['description']
    temp, minTemp, maxTemp = api_response['main']['temp'], api_response['main']['temp_min'], api_response['main']['temp_max']
    pressure, humidity = api_response['main']['pressure'], api_response['main']['humidity']
    wind_speed, wind_deg = api_response['wind']['speed'], api_response['wind']['deg']
    sunrise, sunset = api_response['sys']['sunrise'], api_response['sys']['sunset']

    logger.info(f"Weather in {city}:")
    logger.info(f"  Current Temperature: {kelvin_to_celcius(temp)}° ({kelvin_to_celcius(minTemp)}° min, {kelvin_to_celcius(maxTemp)}° max)")
    logger.info(f"  Wind: {wind_speed} m/s ({wind_deg}°), Pressure: {pressure} hPa, Humidity: {humidity}%")
    logger.info(f"  Sunrise: {unix_to_local_time(sunrise).strftime('%H:%M:%S')} - Sunset: {unix_to_local_time(sunset).strftime('%H:%M:%S')}")
    logger.info("-" * 80)

