import time
import requests

t = time.perf_counter()
r = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": 21.98,
        "longitude": -99.01,
        "current": "temperature_2m"
    },
    timeout=10
)

ms = (time.perf_counter() - t) * 1000
print(r.status_code, f"{ms:.0f} ms", len(r.content))
print(r.json()["current"])
