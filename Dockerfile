# Usa la imagen base completa para asegurar que todas las dependencias se puedan compilar
FROM python:3.10

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# 1. Copia solo el archivo de dependencias e instálalos
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copia todo el contenido de la carpeta 'app' (incluyendo app.py y static/)
#    al directorio de trabajo /app del contenedor.
COPY app /app

# Expone el puerto que usa Flask
EXPOSE 5000

# Usa Gunicorn para iniciar la aplicación (el servidor de producción)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
