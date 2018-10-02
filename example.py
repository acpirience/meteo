from meteopy import meteo


def main():
    # Read API key from file
    with open("openweathermap.api", "r") as key:
        api_key = key.read()

    # run meteo for "Les Sables d'Olonnes" (Id: 6456578) and "Noisy Le Grand" (Id: 6451999)
    meteo.run(api_key, [6456578, 6451999])


if __name__ == "__main__":
    main()
