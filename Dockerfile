FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем API через порт 5000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000"]