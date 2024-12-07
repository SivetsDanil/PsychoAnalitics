# Используем базовый образ Ubuntu
FROM ubuntu:22.04

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    nodejs \
    npm \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем Python зависимости
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Устанавливаем Node.js зависимости
COPY node_project/package*.json /app/node_project/
WORKDIR /app/node_project
RUN npm install

# Возвращаемся в корневую директорию
WORKDIR /app

# Копируем весь проект
COPY . /app

# Открываем порт для Flask приложения
EXPOSE 5000

# Запуск Flask сервиса
CMD ["python3", "main.py"]
