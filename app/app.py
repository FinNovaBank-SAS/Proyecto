from flask import Flask, jsonify, send_file
import datetime
import io
import os # Importar la librería OS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet 
from reportlab.lib.units import inch

app = Flask(__name__)

# --- Lógica de Generación de Reporte (SIN CAMBIOS) ---
def generate_sarlaft_data():
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    
    report_data = {
        "report_id": f"RPT-SARLAFT-{timestamp}",
        "regulator": "UIAF / SARLAFT",
        "date_generated": now.isoformat(),
        "compliance_status": "HIGH",
        "data_summary": {
            "transactions_analyzed": 1500,
            "suspicious_alerts_low": 3,
            "suspicious_alerts_high": 2,
            "reportable_cases": 2
        },
        "regulatory_notes": [
            "El proceso cumple con los requerimientos de la Circular 001 de 2024.",
            "La privacidad de datos está asegurada conforme a Habeas Data."
        ],
        "disclaimer": "Este es un reporte simulado."
    }
    return report_data

# --- NUEVA Lógica de Generación de PDF CON RUTA ABSOLUTA ---
def create_pdf(data):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Estilos de párrafo
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    
    # CRÍTICO: Usar ruta absoluta para asegurar que ReportLab encuentre la imagen.
    # El logo se copia a /app/static/finnova_logo.png
    base_dir = os.path.dirname(os.path.abspath(__file__)) # Obtiene la ruta del script actual (que es /app/app.py)
    # Volvemos un nivel y entramos a static, asumiendo que el logo es PNG
    logo_path = os.path.join(base_dir, 'static', 'finnova_logo.jpg') 
    
    # --- CABECERA Y LOGO ---
    try:
        # Dibujar la imagen
        p.drawImage(logo_path, width - 150, height - 90, width=100, height=50, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        # Si falla el logo, al menos dibuja un título
        print(f"ERROR: No se pudo cargar el logo, verifique formato (PNG/JPG) y ruta: {logo_path}. Error: {e}")
        p.setFont("Helvetica-Bold", 18)
        p.drawString(72, height - 72, "Reporte SARLAFT - FinNova Bank (Logo Faltante)")


    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(colors.darkblue)
    p.drawString(72, height - 72, "Reporte de Cumplimiento SARLAFT")
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.gray)
    p.drawString(72, height - 90, "Generado por FinNova Bank - Automatización Regulatoria")

    # --- SEPARADOR ---
    p.setStrokeColor(colors.lightgrey)
    p.line(72, height - 105, width - 72, height - 105)
    
    y_position = height - 130 # Iniciar contenido principal más abajo
    
    # --- DATOS CLAVE DEL REPORTE ---
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.black)
    p.drawString(72, y_position, "Información General del Reporte:")
    
    p.setFont("Helvetica", 10)
    p.drawString(92, y_position - 20, f"• ID de Reporte: {data['report_id']}")
    p.drawString(92, y_position - 35, f"• Regulador: {data['regulator']}")
    p.drawString(92, y_position - 50, f"• Fecha de Generación: {data['date_generated'][:19].replace('T', ' ')}")
    p.drawString(92, y_position - 65, f"• Estado de Cumplimiento: {data['compliance_status']}")

    # --- RESUMEN DE CUMPLIMIENTO ---
    y_position -= 100
    p.setFont("Helvetica-Bold", 14)
    p.drawString(72, y_position, "Resumen de Datos Analizados:")
    
    p.setFont("Helvetica", 10)
    p.drawString(92, y_position - 20, f"• Transacciones Analizadas: {data['data_summary']['transactions_analyzed']}")
    p.drawString(92, y_position - 35, f"• Alertas Sospechosas (Baja): {data['data_summary']['suspicious_alerts_low']}")
    p.drawString(92, y_position - 50, f"• Alertas Sospechosas (Alta): {data['data_summary']['suspicious_alerts_high']}")
    p.drawString(92, y_position - 65, f"• Casos Reportables a UIAF: {data['data_summary']['reportable_cases']}")
    
    # --- NOTAS REGULATORIAS ---
    y_position -= 100
    p.setFont("Helvetica-Bold", 14)
    p.drawString(72, y_position, "Notas y Observaciones Regulatorias:")
    
    p.setFont("Helvetica", 10)
    line_height = 15
    for i, note in enumerate(data['regulatory_notes']):
        p.drawString(92, y_position - 20 - (i * line_height), f"• {note}")

    # --- DISCLAIMER (Parte inferior) ---
    p.setFillColor(colors.grey)
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(72, 72, data['disclaimer']) # Posición fija en el pie de página

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- ENDPOINTS (SIN CAMBIOS) ---
@app.route('/generate-sarlaft-report', methods=['GET'])
def generate_report():
    data = generate_sarlaft_data()
    pdf_buffer = create_pdf(data)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"SARLAFT_Report_{data['report_id']}.pdf"
    )

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "✅ Servicio de Automatización Regulatoria Activo. Accede a /generate-sarlaft-report para obtener el PDF."
    })
