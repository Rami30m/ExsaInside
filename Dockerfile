# 1️⃣ Базовый образ Python
FROM python:3.11-slim AS backend

WORKDIR /app

# 2️⃣ Устанавливаем зависимости
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3️⃣ Копируем код
COPY backend/ .

# 4️⃣ Запуск FastAPI через uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
