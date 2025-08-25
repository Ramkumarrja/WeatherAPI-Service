from flask import Blueprint, request, jsonify, send_file
from app import db
from app.models import WeatherData
from app.services.weather_service import WeatherService
from app.services.excel_service import ExcelService
from app.services.pdf_service import PDFService

main_bp = Blueprint('main', __name__)

@main_bp.route('/weather-report', methods=['GET'])
def weather_report():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        # Validate required parameters
        if lat is None or lon is None:
            return jsonify({'error': 'Missing required parameters: lat and lon'}), 400
        
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({'error': 'Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180'}), 400
        
        # Fetch and process data
        weather_service = WeatherService()
        raw_data = weather_service.fetch_weather_data(lat, lon)
        processed_data = weather_service.process_weather_data(raw_data, lat, lon)
        
        if not processed_data:
            return jsonify({'error': 'No weather data available for the specified location and time period'}), 404
        
        # Remove existing data for this location to avoid duplicates
        db.session.query(WeatherData).filter(
            WeatherData.latitude == lat,
            WeatherData.longitude == lon
        ).delete()
        
        # Store in database
        records_added = 0
        for data in processed_data:
            weather_record = WeatherData(
                timestamp=data['timestamp'],
                temperature=data['temperature'],
                humidity=data['humidity'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                is_forecast=data.get('is_forecast', False)
            )
            db.session.add(weather_record)
            records_added += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Weather data fetched and stored successfully',
            'records_processed': records_added,
            'latitude': lat,
            'longitude': lon,
            'data_type': 'historical_past_2_days',
            'time_range': f"{processed_data[0]['timestamp'].strftime('%Y-%m-%d %H:%M')} to {processed_data[-1]['timestamp'].strftime('%Y-%m-%d %H:%M')}"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

@main_bp.route('/export/excel', methods=['GET'])
def export_excel():
    try:
        hours = request.args.get('hours', type=int, default=48)
        
        # Get data from database
        from datetime import datetime, timedelta
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        weather_data = WeatherData.query.filter(
            WeatherData.timestamp >= time_threshold
        ).order_by(WeatherData.timestamp).all()
        
        # Generate Excel file
        excel_service = ExcelService()
        excel_file = excel_service.generate_excel(weather_data)
        
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='weather_data.xlsx'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/export/pdf', methods=['GET'])
def export_pdf():
    try:
        hours = request.args.get('hours', type=int, default=48)
        
        # Get data from database
        from datetime import datetime, timedelta
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        weather_data = WeatherData.query.filter(
            WeatherData.timestamp >= time_threshold
        ).order_by(WeatherData.timestamp).all()
        
        # Generate PDF using the alternative service
        pdf_service = PDFService()
        pdf_file = pdf_service.generate_pdf_report(weather_data)
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='weather_report.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'weather-service'})
