FROM python:3.11-slim

WORKDIR /app

COPY . .

# Instala Flask e Gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# Cria pasta de uploads
RUN mkdir -p static/uploads

EXPOSE 5001

# Serve com Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
