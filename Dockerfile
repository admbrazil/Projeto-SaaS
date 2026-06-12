FROM python:3.11-slim

# Dependencias do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collectstatic com settings railway (SECRET_KEY pode ser dummy no build)
RUN SECRET_KEY=dummy-build-key DJANGO_SETTINGS_MODULE=config.settings.railway \
    python manage.py collectstatic --noinput 2>/dev/null || true

# Usuario nao-root por seguranca
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# CMD usa shell form para expandir $PORT corretamente
CMD exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8080}" --workers 2 --timeout 120 --access-logfile -
