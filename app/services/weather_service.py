import requests
from datetime import datetime, timedelta
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    def fetch_weather_data(self, lat, lon):
        """Fetch weather forecast data from Open-Meteo API"""
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m",
            "forecast_days": 7  # Get 7-day forecast
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def process_weather_data(self, raw_data, lat, lon):
        """Process raw API forecast data into structured format"""
        processed_data = []
        hourly = raw_data.get("hourly", {})
        
        # Get the arrays for time, temperature, and humidity
        times = hourly.get("time", [])
        temperatures = hourly.get("temperature_2m", [])
        humidities = hourly.get("relative_humidity_2m", [])
        
        # Check if we have humidity data, if not, set to None
        has_humidity = humidities and len(humidities) == len(times)
        
        for i, timestamp_str in enumerate(times):
            # Handle potential missing humidity data
            humidity = humidities[i] if has_humidity and i < len(humidities) else None
            
            processed_data.append({
                "timestamp": datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')),
                "temperature": temperatures[i] if i < len(temperatures) else None,
                "humidity": humidity,
                "latitude": lat,
                "longitude": lon,
                "is_forecast": True  # Mark as forecast data
            })
        
        return processed_data