import pandas as pd
from io import BytesIO
from flask import send_file

class ExcelService:
    @staticmethod
    def generate_excel(weather_data):
        """Generate Excel file from weather data"""
        data_list = []
        for data in weather_data:
            if hasattr(data, 'to_dict'):
                data_dict = data.to_dict()
                # Handle None values
                data_dict['temperature'] = data_dict.get('temperature', 'N/A')
                data_dict['humidity'] = data_dict.get('humidity', 'N/A')
                data_list.append(data_dict)
            else:
                # Handle dictionary data
                data['temperature'] = data.get('temperature', 'N/A')
                data['humidity'] = data.get('humidity', 'N/A')
                data_list.append(data)
        
        df = pd.DataFrame(data_list)
        
        # Format timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Reorder columns for better readability
        column_order = ['timestamp', 'temperature', 'humidity', 'latitude', 'longitude', 'is_forecast']
        df = df[[col for col in column_order if col in df.columns]]
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Weather Forecast', index=False)
            
            # Format worksheet
            worksheet = writer.sheets['Weather Forecast']
            
            # Set column widths
            column_widths = {
                'A': 20,  # timestamp
                'B': 15,  # temperature
                'C': 15,  # humidity
                'D': 12,  # latitude
                'E': 12,  # longitude
                'F': 12   # is_forecast
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
        
        output.seek(0)
        return output