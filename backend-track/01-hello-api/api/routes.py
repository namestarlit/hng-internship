import logging
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from requests.exceptions import RequestException

from api.config import settings

router = APIRouter()

GEOLOCATION_API_KEY = settings.IPGEOLOCATION_API_KEY
WEATHER_API_KEY = settings.OPENWEATHER_API_KEY

logger = logging.getLogger(__name__)


class Info(BaseModel):
    client_ip: str
    location: str
    greeting: str


def get_location(client_ip: str):
    url = "https://api.ipgeolocation.io/ipgeo"
    payload = {"apiKey": GEOLOCATION_API_KEY, "ip": client_ip, "fields": "city"}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    payload = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


@router.get("/hello", response_model=Info)
async def get_info(*, vistor_name: str | None = "Mark", request: Request) -> Any:
    try:
        client_ip = request.client.host
        location = get_location(client_ip)
        city = location.get("city", "Unkown")
        weather_data = get_weather(city)
        temperature = weather_data["main"]["temp"] if "main" in weather_data else "N/A"
    except RequestException as e:
        logger.error("Error processing the request: {e}")
        raise HTTPException(
            status_code=400, detail=f"Error processing the request: {e}"
        )
    except Exception as e:
        logger.error("An unexpected error occured: {3}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occured")

    response = {
        "client_ip": client_ip,
        "location": city,
        "greeting": f"Hello, {vistor_name}!, the temperature is {temperature} degrees Celsius in {city}",
    }

    return Info(**response)
