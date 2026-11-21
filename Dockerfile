FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes (ej. psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar las dependencias de Python
# Si requirements.txt tiene problemas de codificación (UTF-16 en Windows), 
# descomenta la siguiente línea para convertirlo antes de instalar:
# RUN apt-get install -y dos2unix && dos2unix requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Instalar gunicorn para servir la aplicación en producción
RUN pip install gunicorn

# Copiar el resto del código del proyecto
COPY . .

# Exponer el puerto de Flask/Gunicorn
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
