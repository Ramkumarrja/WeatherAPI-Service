I'll update the README.md with the correct API information. Here's the updated version:

# Weather Report API

A Flask-based backend service that fetches weather forecast data from Open-Meteo API, stores it in SQLite, and provides Excel/PDF export functionality.

## Features

- 🌤️ Fetch 7-day weather forecast data from Open-Meteo API
- 💾 Store weather data in SQLite database
- 📊 Export data to Excel format (.xlsx)
- 📄 Generate PDF reports with charts
- 🐳 Docker container support
- 🚀 RESTful API endpoints

## API Endpoints

### 1. Health Check
- **GET** `/health`
- **Description**: Check if the service is running
- **Response**: 
  ```json
  {
    "status": "healthy",
    "service": "weather-service"
  }
  ```

### 2. Fetch Weather Data
- **GET** `/weather-report?lat={latitude}&lon={longitude}`
- **Parameters**:
  - `lat` (required): Latitude (-90 to 90)
  - `lon` (required): Longitude (-180 to 180)
- **Default**: `lat=52.52&lon=13.41` (Berlin)
- **Response**:
  ```json
  {
    "message": "Weather forecast data fetched and stored successfully",
    "records_processed": 168,
    "latitude": 52.52,
    "longitude": 13.41,
    "data_type": "forecast"
  }
  ```

### 3. Export Excel
- **GET** `/export/excel?hours={hours}`
- **Parameters**:
  - `hours` (optional): Number of hours to export (1-168)
  - **Default**: 48 hours
- **Response**: Excel file (`weather_data.xlsx`) with columns:
  - timestamp | temperature | humidity | latitude | longitude | is_forecast

### 4. Export PDF Report
- **GET** `/export/pdf?hours={hours}`
- **Parameters**:
  - `hours` (optional): Number of hours to include (1-168)
  - **Default**: 48 hours
- **Response**: PDF file (`weather_report.pdf`) containing:
  - Title and metadata
  - Temperature and humidity chart
  - Data table with sample records

## Installation & Setup

### Prerequisites
- Python 3.8+
- Docker (optional)
- Git

### Method 1: Run Locally (without Docker)

```bash
# Clone the repository
git clone <your-repo-url>
cd weather-service-flask

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

The app will start at `http://localhost:5000`

### Method 2: Run with Docker

```bash
# Build and run with Docker
docker build -t weather-app .
docker run -p 5000:5000 weather-app

# Or using docker-compose
docker-compose up
```

## Usage Examples

### Using curl
```bash
# Health check
curl http://localhost:5000/health

# Fetch weather data for Berlin
curl "http://localhost:5000/weather-report?lat=52.52&lon=13.41"

# Fetch weather data for New York
curl "http://localhost:5000/weather-report?lat=40.71&lon=-74.01"

# Export Excel for last 72 hours
curl "http://localhost:5000/export/excel?hours=72" --output weather_data.xlsx

# Export PDF report
curl "http://localhost:5000/export/pdf?hours=48" --output weather_report.pdf
```

### Using Postman
1. Import the Postman collection from `/postman/` folder
2. Set environment variables:
   - `base_url`: `http://localhost:5000`
3. Run requests from the collection

### Using Web Browser
- Health: http://localhost:5000/health
- Weather: http://localhost:5000/weather-report?lat=52.52&lon=13.41
- Excel: http://localhost:5000/export/excel (auto-download)
- PDF: http://localhost:5000/export/pdf (auto-download)

## Example Output Files

### weather_data.xlsx
Contains structured weather data with columns:
- Timestamp (ISO format)
- Temperature (°C)
- Humidity (%)
- Latitude
- Longitude
- Forecast flag

### weather_report.pdf
Contains:
- Professional title and header
- Location metadata and date range
- Interactive temperature/humidity chart
- Sample data table
- Summary statistics

## API Response Structure

The service uses Open-Meteo API which returns:
```json
{
  "latitude": 52.52,
  "longitude": 13.41,
  "hourly": {
    "time": ["2025-08-25T00:00", "2025-08-25T01:00", ...],
    "temperature_2m": [13.1, 12.4, ...],
    "relative_humidity_2m": [73.0, 75.0, ...]
  }
}
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server-side issues

Error responses include descriptive messages:
```json
{
  "error": "Invalid coordinates: latitude must be between -90 and 90"
}
```

## Project Structure

```
weather-service-flask/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py           # SQLAlchemy models
│   ├── routes.py           # API endpoints
│   ├── services/
│   │   ├── weather_service.py    # API data fetching
│   │   ├── excel_service.py      # Excel generation
│   │   └── pdf_service_alt.py    # PDF generation
│   └── config.py           # Configuration
├── instance/
│   └── weather.db          # SQLite database
├── requirements.txt        # Python dependencies
├── run.py                 # Application entry point
├── Dockerfile             # Docker configuration
└── README.md              # This file
```

## Technologies Used

- **Backend**: Flask, Flask-SQLAlchemy
- **Database**: SQLite
- **API Client**: Requests
- **Excel Export**: pandas, openpyxl
- **PDF Generation**: ReportLab, Matplotlib
- **Containerization**: Docker
- **API Documentation**: OpenAPI (via Postman)

## Development

### Running Tests
```bash
# Add tests to the tests/ directory
python -m pytest tests/
```

### Database Management
```bash
# Initialize database (auto-created on first run)
python -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all()"

# View database content
sqlite3 instance/weather.db
```

### Environment Variables
Create a `.env` file for configuration:
```env
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/weather.db
SECRET_KEY=your-secret-key
```

## Support

For issues and questions:
1. Check the Open-Meteo API status: https://open-meteo.com/
2. Review Flask documentation: https://flask.palletsprojects.com/
3. Check existing GitHub issues

## License

MIT License - see LICENSE file for details.

---

**Note**: This service uses the [Open-Meteo Weather API](https://open-meteo.com/) which provides free weather forecast data. Please review their terms of service for usage guidelines.