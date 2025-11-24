# Usa la imagen base completa para asegurar que todas las dependencias se puedan compilar
FROM python:3.10

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de dependencia e instálalos
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación (app/app.py)
COPY app/ .

# Expone el puerto que usa Flask
EXPOSE 5000

# CRÍTICO: Usa Gunicorn para iniciar la aplicación.
# Esto es más robusto y resuelve el "Application exited early".
# 'app:app' significa: ejecutar el objeto Flask llamado 'app' dentro del archivo 'app.py'.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
