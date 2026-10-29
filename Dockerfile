FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8050 DASH_DEBUG=0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El ETL ya dejó los datos limpios en data/processed/; la imagen solo necesita eso y la app.
COPY data/processed ./data/processed
COPY dash_app ./dash_app

EXPOSE 8050
CMD ["sh", "-c", "gunicorn --chdir dash_app app:server --bind 0.0.0.0:${PORT} --workers 2"]
