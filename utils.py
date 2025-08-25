import os
from datetime import datetime
from db import WeatherData
import openpyxl
import matplotlib.pyplot as plt
from weasyprint import HTML

def save_weather_data(session, data):
    times = data.get("hourly", {}).get("time", [])
    temps = data.get("hourly", {}).get("temperature_2m", [])
    hums = data.get("hourly", {}).get("relative_humidity_2m", [])
    for t, temp, hum in zip(times, temps, hums):
        dt = datetime.fromisoformat(t)
        exists = session.query(WeatherData).filter(WeatherData.timestamp == dt).first()
        if not exists:
            wd = WeatherData(timestamp=dt, temperature_2m=temp, relative_humidity_2m=hum)
            session.add(wd)
    session.commit()

def create_excel(rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["timestamp", "temperature_2m", "relative_humidity_2m"])
    for r in rows:
        ws.append([r.timestamp.strftime("%Y-%m-%d %H:%M"), r.temperature_2m, r.relative_humidity_2m])
    file_path = "weather_data.xlsx"
    wb.save(file_path)
    return file_path

def create_pdf(rows):
    times = [r.timestamp for r in rows]
    temps = [r.temperature_2m for r in rows]
    hums = [r.relative_humidity_2m for r in rows]
    plt.figure(figsize=(10,5))
    plt.plot(times, temps, label="Temperature (°C)")
    plt.plot(times, hums, label="Humidity (%)")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.title("Temperature & Humidity (Last 48h)")
    plt.legend()
    chart_path = "chart.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    start = times[0].strftime("%Y-%m-%d %H:%M") if times else ""
    end = times[-1].strftime("%Y-%m-%d %H:%M") if times else ""
    html = f"""
    <h1>Weather Report</h1>
    <p>Location: Provided</p>
    <p>Date Range: {start} - {end}</p>
    <img src="{chart_path}" width="800">
    """
    pdf_path = "weather_report.pdf"
    HTML(string=html, base_url='.').write_pdf(pdf_path)
    os.remove(chart_path)
    return pdf_path
