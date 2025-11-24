# Usa la imagen base completa (no 'slim') para incluir herramientas de compilación
FROM python:3.10

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de dependencia e instálalos
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación (incluyendo app.py)
COPY app/ .

# Expone el puerto que usa Flask
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "app.py"]

