# 1. Используем официальный легкий образ Python
FROM python:3.11-slim

# 2. Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# 3. Копируем файл зависимостей
COPY requirements.txt .

# 4. Устанавливаем библиотеки во внутреннюю систему Docker
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.pythonhosted.org --trusted-host files.pythonhosted.org -r requirements.txt

# 5. Копируем весь остальной код проекта в контейнер
COPY . .

# 6. Открываем порт 5000 для внешнего мира
EXPOSE 5000

# 7. Команда для запуска приложения
CMD ["python", "run.py"]
