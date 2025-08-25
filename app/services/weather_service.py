import requests
from datetime import datetime, timedelta
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        # Use MeteoSwiss API as specified in requirements
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    def fetch_weather_data(self, lat, lon):
        """Fetch weather data from Open-Meteo MeteoSwiss API for past 2 days"""
        # Calculate date range for past 2 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=2)
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "timezone": "auto"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise Exception(f"Failed to fetch weather data: {str(e)}")
    
    def process_weather_data(self, raw_data, lat, lon):
        """Process raw API data into structured format"""
        processed_data = []
        hourly = raw_data.get("hourly", {})
        
        # Get the arrays for time, temperature, and humidity
        times = hourly.get("time", [])
        temperatures = hourly.get("temperature_2m", [])
        humidities = hourly.get("relative_humidity_2m", [])
        
        # Ensure all arrays have the same length
        min_length = min(len(times), len(temperatures), len(humidities))
        
        for i in range(min_length):
            try:
                # Parse timestamp - handle different formats
                timestamp_str = times[i]
                if 'T' in timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
                
                processed_data.append({
                    "timestamp": timestamp,
                    "temperature": temperatures[i] if temperatures[i] is not None else None,
                    "humidity": humidities[i] if humidities[i] is not None else None,
                    "latitude": lat,
                    "longitude": lon,
                    "is_forecast": False  # This is historical data for past 2 days
                })
            except (ValueError, IndexError) as e:
                logger.warning(f"Skipping invalid data point at index {i}: {e}")
                continue
        
        return processed_data
