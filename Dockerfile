FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer puerto si es necesario (ajustar según configuración)
EXPOSE 8000

# Comando para ejecutar el servidor MCP
CMD ["python", "main.py"]
