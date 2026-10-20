from app import create_app

app = create_app()

if __name__ == '__main__':
    # В контейнере обязательно слушаем 0.0.0.0, чтобы сервер принимал внешние запросы
    app.run(host='0.0.0.0', port=5000)
