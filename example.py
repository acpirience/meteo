import logging
from meteopy.meteo import CityMeteo


def main():
    # Logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    )

    # Read API key from file
    with open("openweathermap.api", "r") as key:
        api_key = key.read()

    # run meteo for "Les Sables d'Olonnes" (Id: 6456578)
    les_sables = CityMeteo(api_key, 6456578)
    logging.info("Current weather for les_sables: %s", les_sables.current_weather)
    logging.info("Forecast weather for les_sables: %s", les_sables.forecast_weather)

    for measure_date in les_sables.forecast_weather:
        logging.info("%s => %s", measure_date, les_sables.forecast_weather[measure_date]["temp"])


if __name__ == "__main__":
    main()
