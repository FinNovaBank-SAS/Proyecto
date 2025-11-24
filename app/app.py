from flask import Flask, jsonify, send_file
import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

# --- Lógica de Generación de Reporte ---
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

# --- Lógica de Generación de PDF ---
def create_pdf(data):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 18)
    p.drawString(72, height - 72, "Reporte SARLAFT - FinNova Bank")
    
    p.setFont("Helvetica", 10)
    y_position = height - 100
    
    # Dibujar datos clave
    p.drawString(72, y_position, f"ID de Reporte: {data['report_id']}")
    p.drawString(72, y_position - 15, f"Regulador: {data['regulator']}")
    p.drawString(72, y_position - 30, f"Fecha de Generación: {data['date_generated'][:19]}")
    
    # Dibujar Resumen
    p.setFont("Helvetica-Bold", 12)
    p.drawString(72, y_position - 60, "Resumen de Cumplimiento:")
    
    p.setFont("Helvetica", 10)
    p.drawString(72, y_position - 80, f"Transacciones Analizadas: {data['data_summary']['transactions_analyzed']}")
    p.drawString(72, y_position - 95, f"Alertas Sospechosas (Alta): {data['data_summary']['suspicious_alerts_high']}")
    p.drawString(72, y_position - 110, f"Casos Reportables: {data['data_summary']['reportable_cases']}")
    
    # Dibujar Notas Regulatorias
    p.setFont("Helvetica-Bold", 12)
    p.drawString(72, y_position - 140, "Notas Regulatorias:")
    
    p.setFont("Helvetica", 10)
    line_height = 15
    for i, note in enumerate(data['regulatory_notes']):
        p.drawString(72, y_position - 160 - (i * line_height), f"- {note}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- ENDPOINT DE API (Versión final) ---
@app.route('/generate-sarlaft-report', methods=['GET'])
def generate_report():
    data = generate_sarlaft_data()
    pdf_buffer = create_pdf(data)
    
    # Retorna el PDF como archivo descargable
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"SARLAFT_Report_{data['report_id']}.pdf"
    )

@app.route('/', methods=['GET'])
def home():
    # Mensaje de bienvenida para la raíz
    return jsonify({
        "message": "✅ Servicio de Automatización Regulatoria Activo. Accede a /generate-sarlaft-report para obtener el PDF."
    })
