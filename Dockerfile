FROM python:3.11-slim
 
WORKDIR /app
 
# Instalar LibreOffice + fuentes (fonts-liberation reemplaza Arial en Linux)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice \
        libreoffice-writer \
        fonts-liberation \
        fonts-dejavu \
        fontconfig && \
    fc-cache -fv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . .
 
# Crear carpetas necesarias
RUN mkdir -p minutas_generadas app/templates
 
EXPOSE 8000
 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
