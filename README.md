# 🐳 Микросервисная архитектура с Event-Driven подходом

Учебный проект, демонстрирующий построение отказоустойчивой микросервисной архитектуры с использованием API Gateway, изолированных сервисов и асинхронного брокера сообщений (NATS JetStream).

## 🚀 Быстрый старт

1. Убедитесь, что у вас установлен и запущен **Docker Desktop**.
2. В корне проекта (где лежит `docker-compose.yml`) выполните:
   ```bash
   docker compose up --build -d
   ```
3. Откройте браузер и перейдите по адресу: **http://localhost:8080**.
4. Чтобы увидеть работу событийной модели, откройте логи фронтенда:
   ```bash
   docker compose logs -f frontend-service
   ```

## 📚 Документация

Вся подробная документация проекта находится в папке `docs/`:

*   [Архитектура проекта и UML-диаграммы](docs/architecture.md)
*   [Контракты (HTTP API и события NATS)](docs/contracts.md)
*   **Описание микросервисов:**
    *   [API Gateway](docs/services/gateway.md)
    *   [Auth Backend](docs/services/auth-service.md)
    *   [Frontend Service](docs/services/frontend-service.md)

## 🛠 Технологический стек
*   **Язык:** Python 3.11
*   **Веб-фреймворк:** Flask 3.0.3
*   **ORM:** Flask-SQLAlchemy 3.1.1
*   **Аутентификация:** Flask-Login 0.6.3
*   **Брокер сообщений:** NATS 2.14 (JetStream)
*   **Контейнеризация:** Docker, Docker Compose