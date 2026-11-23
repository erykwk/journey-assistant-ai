import pytest
import respx
import httpx
from src.weather import fetch_weather

@pytest.mark.asyncio
@respx.mock
async def test_fetch_weather_success():
    # Arrange (Przygotowanie)
    latitude = 52.2297
    longitude = 21.0122
    mock_url = "https://api.open-meteo.com/v1/forecast"
    
    # Przykładowa odpowiedź z API, którą nasz mock zwróci zamiast prawdziwego żądania
    mock_response = {
        "current": {
            "temperature_2m": 15.5,
            "wind_speed_10m": 10.0
        }
    }
    
    # Konfiguracja mocka: każde żądanie GET pod ten URL zwróci kod 200 i `mock_response`
    respx.get(mock_url).respond(status_code=200, json=mock_response)
    
    # Act (Działanie)
    result = await fetch_weather(latitude, longitude)
    
    # Assert (Sprawdzenie)
    assert "Temperatura: 15.5°C" in result
    assert "Wiatr: 10.0 km/h" in result

@pytest.mark.asyncio
@respx.mock
async def test_fetch_weather_http_error():
    # Arrange
    latitude = 52.2297
    longitude = 21.0122
    mock_url = "https://api.open-meteo.com/v1/forecast"
    
    # Symulujemy błąd serwera Open-Meteo
    respx.get(mock_url).respond(status_code=500)
    
    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError):
        await fetch_weather(latitude, longitude)
