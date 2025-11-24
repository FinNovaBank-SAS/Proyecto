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
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics

# Pillow (requerido para manejo de imágenes)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finnova_app")


# ---------------------------
# Helpers para el logo
# ---------------------------
def find_logo(base_dir: Path, names=("finnova_logo.jpg", "finnova_logo.jpeg", "finnova_logo.png")) -> Optional[Path]:
    """Busca en base_dir/static por alguno de los nombres y devuelve Path o None."""
    static_dir = base_dir / "static"
    for n in names:
        candidate = static_dir / n
        if candidate.exists():
            return candidate
    return None


def _dump_head_bytes(path: Path, n: int = 64) -> bytes:
    """Devuelve los primeros n bytes del archivo (útil para debug)."""
    try:
        with open(path, "rb") as f:
            return f.read(n)
    except Exception:
        logger.exception("No se pueden leer bytes del logo para debugging")
        return b""


def _load_logo_bytes(logo_path: Optional[Path]) -> Optional[bytes]:
    """
    Lee y devuelve bytes de la imagen listos para ReportLab.
    - Si la imagen es PNG con transparencia (RGBA) la convertimos a JPEG en memoria.
    - Si Pillow falla, retorna None y queda registrado.
    """
    if not logo_path:
        return None
    try:
        raw_head = _dump_head_bytes(logo_path, 16)
        logger.info(f"Logo head bytes (hex): {raw_head.hex() if raw_head else '<empty>'}")

        if not PIL_AVAILABLE:
            # Si Pillow no está disponible intentamos leer crudo
            with open(logo_path, "rb") as f:
                data = f.read()
            return data

        # Intentar abrir con Pillow
        img = Image.open(logo_path)
        logger.info(f"Logo abierto con Pillow: format={img.format}, mode={img.mode}, size={img.size}")

        # Si la imagen tiene transparencia (RGBA/LA/P con transparency), convertimos sobre fondo blanco
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            logger.info("Logo tiene transparencia; convertiremos a JPEG en memoria sobre fondo blanco.")
            rgb = Image.new("RGB", img.size, (255, 255, 255))
            try:
                alpha = img.convert("RGBA").split()[-1]
                rgb.paste(img.convert("RGBA"), mask=alpha)
            except Exception:
                rgb.paste(img.convert("RGBA"))
            out = io.BytesIO()
            rgb.save(out, format="JPEG", quality=95)
            return out.getvalue()
        else:
            # Si no es JPEG, convertimos a JPEG en memoria para máxima compatibilidad
            if img.format != "JPEG":
                out = io.BytesIO()
                img.convert("RGB").save(out, format="JPEG", quality=95)
                return out.getvalue()
            else:
                with open(logo_path, "rb") as f:
                    return f.read()
    except Exception:
        logger.exception("Fallo al cargar/convertir la imagen del logo")
        try:
            head = _dump_head_bytes(logo_path, 64)
            logger.error(f"Primeros 64 bytes del archivo logo (hex): {head.hex() if head else '<empty>'}")
        except Exception:
            pass
        return None


# --- Lógica de Generación de Datos ---
def generate_sarlaft_data():
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    return {
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


# --- Lógica de Generación de PDF (con control de solapamiento título/logo) ---
def create_pdf(data) -> io.BytesIO:
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()

    base_dir = Path(__file__).resolve().parent
    logger.info(f"base_dir = {base_dir}")
    logo_path = find_logo(base_dir)
    if logo_path:
        logger.info(f"Logo encontrado: {logo_path}")
    else:
        logger.warning("Logo NO encontrado en 'static/'")

    # Cargar logo como bytes y preparar ImageReader
    logo_bytes = _load_logo_bytes(logo_path)

    # --- DIBUJAR LOGO en esquina superior derecha (si existe) ---
    logo_drawn = False
    logo_x = logo_y = draw_w = draw_h = 0
    if logo_bytes:
        try:
            img_reader = ImageReader(io.BytesIO(logo_bytes))
            iw, ih = img_reader.getSize()

            # tamaño máximo del logo en pts (ajusta si quieres más grande/pequeño)
            max_w = 120
            scale = max_w / float(iw) if iw > 0 else 1.0
            draw_w = max_w
            draw_h = int(ih * scale)

            # Márgenes
            right_margin = 72  # pts
            top_margin = 36    # pts desde la parte superior

            # calcular coordenadas: drawImage usa la esquina inferior izquierda (x, y)
            logo_x = width - right_margin - draw_w
            logo_top = height - top_margin
            logo_y = logo_top - draw_h

            # Dibujar logo
            p.drawImage(img_reader, logo_x, logo_y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask='auto')
            logo_drawn = True
            logger.info(f"Logo dibujado en: x={logo_x}, y={logo_y}, w={draw_w}, h={draw_h}")
        except Exception:
            logger.exception("Error al dibujar el logo; se continuará sin logo.")
            logo_drawn = False

    # --- DIBUJAR TITULO evitando solapamiento ---
    title_text = "Reporte de Cumplimiento SARLAFT"
    title_font = "Helvetica-Bold"
    title_font_size = 24
    p.setFont(title_font, title_font_size)
    p.setFillColor(colors.darkblue)

    # Posición default del título (izquierda, cercano a la parte superior)
    title_x = 72
    title_y_default = height - 96  # baseline por defecto
    title_x = 72
    title_y = title_y_default

    # calcular ancho/alto aproximado del texto
    title_width = pdfmetrics.stringWidth(title_text, title_font, title_font_size)
    title_height = title_font_size  # aproximación para bounding height

    if logo_drawn:
        # bounding boxes:
        title_top = title_y + title_height
        title_bottom = title_y
        title_left = title_x
        title_right = title_x + title_width

        logo_left = logo_x
        logo_right = logo_x + draw_w
        logo_bottom = logo_y
        logo_top = logo_y + draw_h

        # Detectar solapamiento horizontal y vertical
        horizontal_overlap = not (title_right < logo_left or title_left > logo_right)
        vertical_overlap = not (title_top < logo_bottom or title_bottom > logo_top)

        if horizontal_overlap and vertical_overlap:
            # ajustar: bajar el título por debajo del logo (logo_bottom - titulo_altura - padding)
            padding = 8  # pts
            new_title_y = logo_bottom - title_height - padding
            # Si el nuevo título queda muy abajo, limitamos (opcional)
            min_y_allowed = 72 + title_height  # no bajar más del pie
            if new_title_y < min_y_allowed:
                new_title_y = min_y_allowed
            logger.info(f"Titulo solapaba logo. Moviendo titulo de y={title_y} a y={new_title_y}")
            title_y = new_title_y
        else:
            logger.info("Titulo no solapa con logo; mantenemos posición por defecto.")
    else:
        logger.info("No hay logo dibujado; título usa posición por defecto.")

    # Dibujar título y subtítulo
    p.setFont(title_font, title_font_size)
    p.setFillColor(colors.darkblue)
    p.drawString(title_x, title_y, title_text)

    subtitle_y = title_y - 18  # 18 pts debajo del baseline del título
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.gray)
    p.drawString(72, subtitle_y, "Generado por FinNova Bank - Automatización Regulatoria")

    # Separador
    p.setStrokeColor(colors.lightgrey)
    p.line(72, subtitle_y - 8, width - 72, subtitle_y - 8)

    # Contenido principal (ajusta y_position relativo al subtitle)
    y_position = subtitle_y - 36

    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.black)
    p.drawString(72, y_position, "Información General del Reporte:")

    p.setFont("Helvetica", 10)
    p.drawString(92, y_position - 20, f"• ID de Reporte: {data['report_id']}")
    p.drawString(92, y_position - 35, f"• Regulador: {data['regulator']}")
    p.drawString(92, y_position - 50, f"• Fecha de Generación: {data['date_generated'][:19].replace('T', ' ')}")
    p.drawString(92, y_position - 65, f"• Estado de Cumplimiento: {data['compliance_status']}")

    # Resumen
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

    # Disclaimer pie
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
    try:
        data = generate_sarlaft_data()
        pdf_buffer = create_pdf(data)
        download_name = f"SARLAFT_Report_{data['report_id']}.pdf"
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=download_name)
    except Exception:
        logger.exception("Error generando PDF")
        return make_response(jsonify({"error": "Error generando PDF"}), 500)


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "✅ Servicio de Automatización Regulatoria Activo. Accede a /generate-sarlaft-report para obtener el PDF."})


if __name__ == '__main__':
    # Modo debug local solamente
    app.run(host='0.0.0.0', port=5000, debug=True)
