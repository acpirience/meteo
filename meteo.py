import requests
from yaml import load, dump
import logging

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
with open("config.yml") as yml_file:
    config = load(yml_file)
    logger.info("YAML configuration loaded")


