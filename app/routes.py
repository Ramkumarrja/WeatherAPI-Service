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
        lat = request.args.get('lat', type=float, default=52.52)  # Default to Berlin
        lon = request.args.get('lon', type=float, default=13.41)  # Default to Berlin
        
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({'error': 'Invalid coordinates'}), 400
        
        # Fetch and process data
        weather_service = WeatherService()
        raw_data = weather_service.fetch_weather_data(lat, lon)
        processed_data = weather_service.process_weather_data(raw_data, lat, lon)
        
        # Store in database
        for data in processed_data:
            weather_record = WeatherData(
                timestamp=data['timestamp'],
                temperature=data['temperature'],
                humidity=data['humidity'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                is_forecast=data.get('is_forecast', True)  # Default to True for forecast
            )
            db.session.add(weather_record)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Weather forecast data fetched and stored successfully',
            'records_processed': len(processed_data),
            'latitude': lat,
            'longitude': lon,
            'data_type': 'forecast'
        })
        
    except Exception as e:
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