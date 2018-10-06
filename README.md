# `Meteo`

Example of using the meteo API of [Openweathermap](https://openweathermap.org/api)

```python
from meteopy.meteo import CityMeteo

# run meteo for "Paris France" (Id: 6456578)
paris = CityMeteo("your_openweathermap_api_key", 6456578)
print("Current weather for les_sables: %s", paris.current_weather)
print("Forecast weather for les_sables: %s", paris.forecast_weather)

for measure_date in paris.forecast_weather:
    print("%s => %s", measure_date, paris.forecast_weather[measure_date]["temp"])


```