# `Meteo`

Example of using the meteo API of [Openweathermap](https://openweathermap.org/api)

```python
from meteopy import meteo

# run meteo for "Paris France" (Id: 6456578) and "Paris Canada" (Id:6942553)
meteo.run("your_openweathermap_api_key", [6456578, 6942553])

```