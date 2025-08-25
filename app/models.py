from app import db
from datetime import datetime

class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    temperature = db.Column(db.Float, nullable=True)  # Allow null for missing data
    humidity = db.Column(db.Float, nullable=True)     # Allow null for missing data
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    is_forecast = db.Column(db.Boolean, default=False)  # Track if it's forecast data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_forecast': self.is_forecast,
            'created_at': self.created_at.isoformat()
        }