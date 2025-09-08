FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# deps de sistema para mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    default-mysql-client \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# dependencias Python
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# copiar proyecto
COPY . .

# asegurar carpeta MEDIA_ROOT dentro del contenedor
RUN mkdir -p /app/files

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
