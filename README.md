# Weather API Service

A Flask-based REST API service that fetches weather data from the Open-Meteo MeteoSwiss API, stores it in a SQLite database, and provides endpoints to export data in Excel and PDF formats with charts.

## Features

- **Weather Data Fetching**: Retrieves temperature and humidity data for the past 2 days from Open-Meteo MeteoSwiss API
- **REST API Endpoints**: 
  - `GET /weather-report?lat={lat}&lon={lon}` - Fetch and store weather data
  - `GET /export/excel` - Export data to Excel format (.xlsx)
  - `GET /export/pdf` - Export data to PDF with charts
  - `GET /health` - Health check endpoint
- **Data Storage**: SQLite database with proper indexing
- **Excel Export**: Professional Excel files with metadata and styling
- **PDF Reports**: PDF reports with matplotlib charts using ReportLab (Windows compatible)
- **Docker Support**: Fully containerized application

## Requirements

- Python 3.11+
- Flask 2.3.3
- SQLAlchemy 2.0.23
- WeasyPrint 61.2
- Matplotlib 3.8.2
- OpenPyXL 3.1.2
- Docker & Docker Compose (for containerized deployment)

## Installation & Setup

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd WeatherAPI-Service
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The service will be available at `http://localhost:5000`

### Option 2: Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd WeatherAPI-Service
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python run.py
```

The service will be available at `http://localhost:5000`

## API Usage

### 1. Fetch Weather Data

Fetch weather data for the past 2 days and store in database:

```bash
curl "http://localhost:5000/weather-report?lat=47.37&lon=8.55"
```

**Parameters:**
- `lat` (required): Latitude (-90 to 90)
- `lon` (required): Longitude (-180 to 180)

**Response:**
```json
{
  "message": "Weather data fetched and stored successfully",
  "records_processed": 48,
  "latitude": 47.37,
  "longitude": 8.55,
  "data_type": "historical_past_2_days",
  "time_range": "2024-01-01 00:00 to 2024-01-03 00:00"
}
```

### 2. Export to Excel

Export the last 48 hours of data to Excel format:

```bash
curl "http://localhost:5000/export/excel" -o weather_data.xlsx
```

**Optional Parameters:**
- `hours` (default: 48): Number of hours of data to export

**Output:** `weather_data.xlsx` with:
- Weather data sheet with columns: timestamp | temperature_2m | relative_humidity_2m
- Metadata sheet with statistics and information

### 3. Export to PDF

Export the last 48 hours of data to PDF with charts:

```bash
curl "http://localhost:5000/export/pdf" -o weather_report.pdf
```

**Optional Parameters:**
- `hours` (default: 48): Number of hours of data to export

**Output:** `weather_report.pdf` with:
- Title & metadata (location, date range)
- Line chart showing temperature & humidity vs time
- Sample data table

### 4. Health Check

Check service status:

```bash
curl "http://localhost:5000/health"
```

## Example Usage Workflow

1. **Fetch data for Zurich, Switzerland:**
```bash
curl "http://localhost:5000/weather-report?lat=47.37&lon=8.55"
```

2. **Export to Excel:**
```bash
curl "http://localhost:5000/export/excel" -o weather_data.xlsx
```

3. **Export to PDF:**
```bash
curl "http://localhost:5000/export/pdf" -o weather_report.pdf
```

## Project Structure

```
WeatherAPI-Service/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── models.py            # Database models
│   ├── routes.py            # API endpoints
│   └── services/
│       ├── weather_service.py  # Weather API integration
│       ├── excel_service.py    # Excel export functionality
│       └── pdf_service.py      # PDF report generation
├── instance/
│   └── weather.db           # SQLite database (auto-created)
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile              # Docker image configuration
├── requirements.txt        # Python dependencies
├── run.py                 # Application entry point
└── README.md              # This file
```

## Database Schema

**WeatherData Table:**
- `id`: Primary key
- `timestamp`: DateTime (indexed)
- `temperature`: Float (°C)
- `humidity`: Float (%)
- `latitude`: Float
- `longitude`: Float
- `is_forecast`: Boolean
- `created_at`: DateTime

## API Specifications

The service uses the **Open-Meteo MeteoSwiss API**:
- Base URL: `https://api.open-meteo.com/v1/meteoswiss`
- Parameters: `latitude`, `longitude`, `hourly=temperature_2m,relative_humidity_2m`
- Data Range: Past 2 days from current date

## Error Handling

The API provides comprehensive error handling:
- **400 Bad Request**: Invalid parameters or coordinates
- **404 Not Found**: No data available for specified location/time
- **500 Internal Server Error**: Server-side errors with detailed messages

## Development

### Running Tests

```bash
# Add your test commands here
python -m pytest tests/
```

### Environment Variables

- `FLASK_ENV`: Set to `development` for debug mode
- `FLASK_DEBUG`: Set to `1` for debug mode

## Docker Configuration

The application is fully containerized with:
- **Base Image**: Python 3.11-slim
- **System Dependencies**: WeasyPrint requirements (Cairo, Pango, etc.)
- **Port**: 5000
- **Volumes**: Code and database persistence
- **Auto-restart**: Unless stopped

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
