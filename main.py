from fastapi import FastAPI, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import requests
import os

from db import SessionLocal, Base, engine, WeatherData
from utils import save_weather_data, create_excel, create_pdf

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/weather-report")
def weather_report(lat: float = Query(...), lon: float = Query(...)):
    end = datetime.utcnow()
    start = end - timedelta(days=2)
    url = (
        f"https://api.open-meteo.com/v1/meteoswiss?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,relative_humidity_2m"
        f"&start={start.strftime('%Y-%m-%dT%H:%M')}"
        f"&end={end.strftime('%Y-%m-%dT%H:%M')}"
        f"&timezone=UTC"
    )
    resp = requests.get(url)
    data = resp.json()
    session = SessionLocal()
    save_weather_data(session, data)
    session.close()
    return {"status": "success", "count": len(data.get("hourly", {}).get("time", []))}

@app.get("/export/excel")
def export_excel():
    session = SessionLocal()
    end = datetime.utcnow()
    start = end - timedelta(hours=48)
    rows = session.query(WeatherData).filter(WeatherData.timestamp >= start).order_by(WeatherData.timestamp).all()
    session.close()
    file_path = create_excel(rows)
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="weather_data.xlsx")

@app.get("/export/pdf")
def export_pdf():
    session = SessionLocal()
    end = datetime.utcnow()
    start = end - timedelta(hours=48)
    rows = session.query(WeatherData).filter(WeatherData.timestamp >= start).order_by(WeatherData.timestamp).all()
    session.close()
    file_path = create_pdf(rows)
    return FileResponse(file_path, media_type="application/pdf", filename="weather_report.pdf")
