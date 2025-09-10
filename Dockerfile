FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt

COPY . .


# На старте: миграции + runserver на $PORT
CMD sh -c "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:${PORT:-8000}"