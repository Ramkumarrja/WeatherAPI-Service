from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
import matplotlib.dates as mdates

class PDFService:
    def __init__(self):
        # Register fonts if needed
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        except:
            pass  # Use default font if Arial not available

    def generate_pdf_report(self, weather_data):
        """Generate PDF report with chart and data table"""
        if not weather_data:
            return self._generate_empty_pdf()
        
        # Create buffer for PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Story elements
        story = []
        
        # Add title
        title = Paragraph("WEATHER DATA REPORT", title_style)
        story.append(title)
        
        # Add metadata
        metadata_text = self._generate_metadata_text(weather_data)
        metadata = Paragraph(metadata_text, styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Add chart
        chart_buffer = self._create_chart(weather_data)
        if chart_buffer:
            chart_img = Image(chart_buffer, width=6*inch, height=4*inch)
            story.append(chart_img)
            story.append(Spacer(1, 20))
        
        # Add data table
        table_data = self._create_table_data(weather_data)
        if table_data:
            table = Table(table_data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def _generate_metadata_text(self, weather_data):
        """Generate metadata text for PDF"""
        if not weather_data:
            return "No weather data available"
            
        sample = weather_data[0]
        first_date = weather_data[0].timestamp.strftime('%Y-%m-%d %H:%M')
        last_date = weather_data[-1].timestamp.strftime('%Y-%m-%d %H:%M')
        
        # Count available data points
        temp_count = sum(1 for d in weather_data if d.temperature is not None)
        humidity_count = sum(1 for d in weather_data if d.humidity is not None)
        
        metadata_text = f"""
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>
        <b>Location:</b> Latitude: {sample.latitude}, Longitude: {sample.longitude}<br/>
        <b>Forecast Period:</b> {first_date} to {last_date}<br/>
        <b>Total Records:</b> {len(weather_data)} hours<br/>
        <b>Temperature Data Points:</b> {temp_count}<br/>
        <b>Humidity Data Points:</b> {humidity_count}<br/>
        """
        
        # Add temperature range if available
        valid_temps = [d.temperature for d in weather_data if d.temperature is not None]
        if valid_temps:
            metadata_text += f"<b>Temperature Range:</b> {min(valid_temps):.1f}°C to {max(valid_temps):.1f}°C<br/>"
        
        # Add humidity range if available
        valid_humidities = [d.humidity for d in weather_data if d.humidity is not None]
        if valid_humidities:
            metadata_text += f"<b>Humidity Range:</b> {min(valid_humidities):.1f}% to {max(valid_humidities):.1f}%<br/>"
        
        metadata_text += f"<b>Data Type:</b> {'Forecast' if getattr(sample, 'is_forecast', False) else 'Historical'}<br/>"
        
        return metadata_text

    def _create_chart(self, weather_data):
        """Create matplotlib chart for temperature and humidity"""
        try:
            timestamps = [d.timestamp for d in weather_data]
            temperatures = [d.temperature for d in weather_data]
            humidities = [d.humidity for d in weather_data]
            
            fig, ax1 = plt.subplots(figsize=(10, 6))
            
            # Plot temperature
            color = 'tab:red'
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Temperature (°C)', color=color, fontweight='bold')
            line1 = ax1.plot(timestamps, temperatures, color=color, linewidth=2, label='Temperature')
            ax1.tick_params(axis='y', labelcolor=color)
            
            # Plot humidity on second axis
            ax2 = ax1.twinx()
            color = 'tab:blue'
            ax2.set_ylabel('Humidity (%)', color=color, fontweight='bold')
            line2 = ax2.plot(timestamps, humidities, color=color, linewidth=2, label='Humidity')
            ax2.tick_params(axis='y', labelcolor=color)
            
            # Format x-axis dates
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax1.xaxis.set_major_locator(mdates.HourLocator(interval=6))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # Add title and grid
            plt.title('Temperature and Humidity Trends', fontweight='bold', pad=20)
            ax1.grid(True, alpha=0.3)
            
            # Add legend
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc='upper left')
            
            plt.tight_layout()
            
            # Save to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            plt.close(fig)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"Chart creation error: {e}")
            return None

    def _create_table_data(self, weather_data):
        """Create table data for PDF"""
        table_data = [
            ['Timestamp', 'Temp (°C)', 'Humidity (%)']
        ]
        
        # Add sample data (first 10 records)
        for data in weather_data[:10]:
            table_data.append([
                data.timestamp.strftime('%m-%d %H:%M'),
                f'{data.temperature:.1f}',
                f'{data.humidity:.1f}'
            ])
        
        if len(weather_data) > 10:
            table_data.append(['...', '...', '...'])
        
        return table_data

    def _generate_empty_pdf(self):
        """Generate PDF when no data is available"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        story = [
            Paragraph("WEATHER DATA REPORT", styles['Title']),
            Spacer(1, 20),
            Paragraph("No weather data available for the selected time period.", styles['Normal']),
            Spacer(1, 20),
            Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal'])
        ]
        
        doc.build(story)
        buffer.seek(0)
        return buffer