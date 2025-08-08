# Usamos una imagen ligera de Python
FROM python:3.12-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos archivos de dependencias e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto que usará Uvicorn
EXPOSE 8000

# Comando por defecto para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]