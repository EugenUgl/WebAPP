# 🏗 Архитектура проекта

Этот документ описывает общую структуру проекта, логическое и физическое взаимодействие компонентов.

## 📁 Структура проекта

```text
WebAPP/
├── docker-compose.yml       # Оркестрация контейнеров
├── README.md                # Главная страница документации
├── docs/                    # Данная папка с документацией
├── gateway/                 # API Gateway (точка входа)
│   ├── Dockerfile
│   └── gateway.py
├── frontend-service/        # Микросервис UI
│   ├── Dockerfile
│   └── app.py
└── flask-auth-service/      # Микросервис авторизации
    ├── app/
    │   ├── __init__.py      # Инициализация Flask и БД
    │   ├── events.py        # Публикация событий в NATS
    │   ├── models.py        # Модель User
    │   └── routes.py        # HTTP-маршруты
    ├── Dockerfile
    ├── requirements.txt
    └── run.py
```

## 🧩 Компонентная UML-диаграмма (Component Diagram)

Показывает логические блоки системы и направления их взаимодействия.

```mermaid
flowchart TD
    Client([Клиент / Браузер])
    
    subgraph System["Микросервисная система"]
        GW["API Gateway\n(Port 80)"]
        FE["Frontend Service\n(Port 5000)"]
        AU["Auth Backend\n(Port 5000)"]
        NATS[("NATS JetStream\n(Port 4222)")]
        DB[("SQLite DB")]
    end

    Client -->|HTTP :8080| GW
    GW -->|Маршрут: /| FE
    GW -->|Маршрут: /login, /register| AU
    
    AU -->|Публикация: user.registered| NATS
    NATS -->|Подписка: user.registered| FE
    
    AU -->|SQLAlchemy| DB
    
    classDef client fill:#f9f,stroke:#333,stroke-width:2px;
    classDef service fill:#bbf,stroke:#333,stroke-width:2px;
    classDef broker fill:#fbb,stroke:#333,stroke-width:2px;
    classDef db fill:#bfb,stroke:#333,stroke-width:2px;
    
    class Client client;
    class GW,FE,AU service;
    class NATS broker;
    class DB db;
```

## 🐳 Диаграмма развертывания (Deployment UML)

Отражает физическое размещение контейнеров в Docker-сети и проброс портов.

```mermaid
flowchart TB
    subgraph Host["Хост-машина (Windows/Mac/Linux)"]
        Port8080((Порт 8080))
        
        subgraph Docker["Docker Compose: microservice_network"]
            GW_C[Контейнер: microservice-gateway]
            FE_C[Контейнер: microservice-frontend]
            AU_C[Контейнер: microservice-auth-backend]
            NATS_C[Контейнер: microservice-nats]
            
            Vol[(Volume: ./instance)]
        end
    end
    
    Port8080 --> GW_C
    GW_C --> FE_C
    GW_C --> AU_C
    AU_C --> NATS_C
    FE_C --> NATS_C
    AU_C -.->|Хранит данные| Vol
```