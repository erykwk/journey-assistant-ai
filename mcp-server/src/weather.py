import httpx

async def fetch_weather(latitude: float, longitude: float) -> str:
    """
    Pobiera obecną prognozę pogody dla podanych współrzędnych za pomocą Open-Meteo.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m"
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        temp = current.get("temperature_2m", "N/A")
        wind = current.get("wind_speed_10m", "N/A")
        
        return f"Temperatura: {temp}°C, Wiatr: {wind} km/h"
