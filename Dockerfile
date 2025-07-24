FROM python:3.12

WORKDIR /app

# Устанавливаем компиляторы и CMake
RUN apt-get update && apt-get install -y \
    gcc g++ cmake make curl \
    && apt-get clean

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

