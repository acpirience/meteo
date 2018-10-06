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

    # run meteo for "Les Sables d'Olonnes" (Id: 6456578) and "Noisy Le Grand" (Id: 6451999)
    les_sables = CityMeteo(api_key, 6456578)
    noisy = CityMeteo(api_key, 6451999)
    les_sables.run()
    noisy.run()


if __name__ == "__main__":
    main()
