# app.py
import io
import datetime
import logging
from pathlib import Path
from typing import Optional

from flask import Flask, jsonify, send_file, make_response
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Si usas Pillow para inspeccionar imágenes (opcional pero recomendado)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

app = Flask(__name__)

# Configurar logging simple
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finnova_app")


# ---------------------------
# Helpers
# ---------------------------
def find_logo(base_dir: Path, names=("finnova_logo.jpg", "finnova_logo.jpeg", "finnova_logo.png")) -> Optional[Path]:
    """
    Busca en base_dir/static por alguno de los nombres en 'names' y devuelve la Path
    si existe, o None si no se encuentra.
    """
    static_dir = base_dir / "static"
    for n in names:
        candidate = static_dir / n
        if candidate.exists():
            return candidate
    return None


# --- Lógica de Generación de Datos ---
def generate_sarlaft_data():
    """Genera datos simulados para el reporte SARLAFT."""
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
        "disclaimer": "Este es un reporte simulado. El objetivo es la prueba de la infraestructura CI/CD."
    }
    return report_data


# --- Lógica de Generación de PDF ---
def create_pdf(data) -> io.BytesIO:
    """
    Crea el PDF en memoria y lo devuelve como BytesIO listo para send_file.
    """

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    styles = getSampleStyleSheet()

    # Construir ruta absoluta en base a la ubicación de este archivo.
    base_dir = Path(__file__).resolve().parent  # normalmente /app dentro del contenedor
    logo_path = find_logo(base_dir)

    logger.info(f"base_dir = {base_dir}")
    if logo_path:
        logger.info(f"Logo encontrado: {logo_path}")
    else:
        logger.warning("Logo NO encontrado en 'static/'. Se generará el PDF sin logo.")

    # --- CABECERA Y LOGO ---
    try:
        if logo_path:
            # Si Pillow está disponible podemos conocer tamaño y mantener proporciones
            if PIL_AVAILABLE:
                try:
                    img = Image.open(logo_path)
                    w_px, h_px = img.size
                    # Queremos dibujar un logo no mayor a 120 puntos de ancho
                    max_w = 120
                    draw_w = max_w
                    draw_h = int(h_px * (draw_w / w_px))
                except Exception:
                    # fallback dimensiones
                    draw_w, draw_h = 100, 50
            else:
                draw_w, draw_h = 100, 50

            # Ubicar a la derecha en la cabecera (márgenes: 72 pts)
            p.drawImage(str(logo_path), width - 72 - draw_w, height - 72 - (draw_h // 2),
                        width=draw_w, height=draw_h, preserveAspectRatio=True, mask='auto')
        else:
            # Si no hay logo, escribir aviso en la cabecera
            p.setFont("Helvetica-Bold", 18)
            p.drawString(72, height - 72, "Reporte SARLAFT - FinNova Bank (¡SIN LOGO!)")
    except Exception as e:
        # No queremos que la ausencia o fallo del logo impida crear el PDF
        logger.exception("Error al dibujar el logo, continuando sin logo.")
        p.setFont("Helvetica-Bold", 18)
        p.drawString(72, height - 72, "Reporte SARLAFT - FinNova Bank (¡SIN LOGO!)")

    # Título y subtítulo
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(colors.darkblue)
    p.drawString(72, height - 96, "Reporte de Cumplimiento SARLAFT")

    p.setFont("Helvetica", 10)
    p.setFillColor(colors.gray)
    p.drawString(72, height - 112, "Generado por FinNova Bank - Automatización Regulatoria")

    # Separador
    p.setStrokeColor(colors.lightgrey)
    p.line(72, height - 128, width - 72, height - 128)

    y_position = height - 156  # iniciar contenido principal

    # Información general
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.black)
    p.drawString(72, y_position, "Información General del Reporte:")

    p.setFont("Helvetica", 10)
    p.drawString(92, y_position - 20, f"• ID de Reporte: {data['report_id']}")
    p.drawString(92, y_position - 35, f"• Regulador: {data['regulator']}")
    p.drawString(92, y_position - 50, f"• Fecha de Generación: {data['date_generated'][:19].replace('T', ' ')}")
    p.drawString(92, y_position - 65, f"• Estado de Cumplimiento: {data['compliance_status']}")

    # Resumen de datos analizados
    y_position -= 100
    p.setFont("Helvetica-Bold", 14)
    p.drawString(72, y_position, "Resumen de Datos Analizados:")

    p.setFont("Helvetica", 10)
    p.drawString(92, y_position - 20, f"• Transacciones Analizadas: {data['data_summary']['transactions_analyzed']}")
    p.drawString(92, y_position - 35, f"• Alertas Sospechosas (Baja): {data['data_summary']['suspicious_alerts_low']}")
    p.drawString(92, y_position - 50, f"• Alertas Sospechosas (Alta): {data['data_summary']['suspicious_alerts_high']}")
    p.drawString(92, y_position - 65, f"• Casos Reportables a UIAF: {data['data_summary']['reportable_cases']}")

    # Notas regulatorias
    y_position -= 100
    p.setFont("Helvetica-Bold", 14)
    p.drawString(72, y_position, "Notas y Observaciones Regulatorias:")

    p.setFont("Helvetica", 10)
    line_height = 15
    for i, note in enumerate(data['regulatory_notes']):
        p.drawString(92, y_position - 20 - (i * line_height), f"• {note}")

    # Disclaimer al pie
    p.setFillColor(colors.gray)
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(72, 72, data['disclaimer'])

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


# ---------------------------
# Endpoints
# ---------------------------
@app.route('/generate-sarlaft-report', methods=['GET'])
def generate_report():
    """Endpoint para generar y descargar el PDF."""
    try:
        data = generate_sarlaft_data()
        pdf_buffer = create_pdf(data)

        # Construir nombre del archivo
        download_name = f"SARLAFT_Report_{data['report_id']}.pdf"

        # send_file acepta un file-like; Flask 2.0+ soporta download_name
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        logger.exception("Error generando PDF")
        return make_response(jsonify({"error": "Error generando PDF", "detail": str(e)}), 500)


@app.route('/', methods=['GET'])
def home():
    """Endpoint principal de prueba."""
    return jsonify({
        "message": "✅ Servicio de Automatización Regulatoria Activo. Accede a /generate-sarlaft-report para obtener el PDF."
    })


# Ejecutar en modo desarrollo (no se usa en producción dentro del contenedor con gunicorn)
if __name__ == '__main__':
    # Modo debug local solamente
    app.run(host='0.0.0.0', port=5000, debug=True)

