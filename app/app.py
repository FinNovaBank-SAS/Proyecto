from flask import Flask, jsonify, send_file
import json
from datetime import datetime
import io

app = Flask(__name__)

def generate_regulatory_report():
    report_data = {
        "report_id": f"RPT-SARLAFT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "regulator": "UIAF / SARLAFT",
        "date_generated": datetime.now().isoformat(),
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

@app.route('/')
def home():
    return jsonify({"message": "✅ Servicio de Automatización Regulatoria Activo. Accede a /generate-sarlaft-report."})

@app.route('/generate-sarlaft-report', methods=['GET'])
def generate_report():
    report = generate_regulatory_report()
    output = io.StringIO()
    json.dump(report, output, indent=4)
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.read().encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name='sarlaft_report.json'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)