from flask import Flask, render_template_string
import asyncio
import nats
import json
import threading
import logging

app = Flask(__name__)

HTML_INDEX = """
<!DOCTYPE html>
<html>
<head>
    <title>Главная страница микросервисов</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background-color: #f4f4f9; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; }
        .btn { display: inline-block; padding: 10px 20px; margin: 10px; text-decoration: none; color: white; background: #007bff; border-radius: 5px; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Добро пожаловать в Microservices App!</h1>
        <p>Этот лендинг отдается отдельным микросервисом (Frontend).</p>
        <p>Авторизация обрабатывается другим микросервисом (Auth Backend) через API Gateway.</p>
        <a href="/login" class="btn">Войти</a>
        <a href="/register" class="btn">Зарегистрироваться</a>
    </div>
</body>
</html>
"""

# --- Логика слушателя NATS JetStream ---

async def message_handler(msg):
    data = json.loads(msg.data.decode())
    print(f"\n[Frontend] 🎉 ПОЛУЧЕНО СОБЫТИЕ от NATS JetStream!")
    print(f"[Frontend] Новый пользователь: {data.get('username')}\n")
    await msg.ack() # Подтверждаем обработку сообщения

async def listen_to_nats():
    # Даем NATS время на запуск
    await asyncio.sleep(3)
    try:
        nc = await nats.connect("nats://nats:4222")
        js = nc.jetstream()

        # Подписываемся на поток. Durable означает, что мы запомним,
        # на каком сообщении остановились, если контейнер перезагрузится.
        sub = await js.pull_subscribe(
            subject="user.registered",
            durable="frontend_consumer",
            stream="USER_EVENTS"
        )
        print("[Frontend] Успешно подключились к NATS. Слушаем события...")
        
        while True:
            try:
                # Ждем до 1 секунды пачку из 1 сообщения
                msgs = await sub.fetch(batch=1, timeout=1)
                for msg in msgs:
                    await message_handler(msg)
            except asyncio.TimeoutError:
                continue # Сообщений нет, идем на новый круг
            except Exception as e:
                print(f"Ошибка в цикле слушателя: {e}")
                await asyncio.sleep(1)
    except Exception as e:
        print(f"[Frontend] Не удалось подключиться к NATS: {e}")

def run_nats_listener():
    # Запускаем бесконечный асинхронный цикл в отдельном потоке
    asyncio.run(listen_to_nats())

# Стартуем фоновый поток ДО запуска Flask
threading.Thread(target=run_nats_listener, daemon=True).start()

# --- Маршруты Flask ---

@app.route('/')
def index():
    return render_template_string(HTML_INDEX)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)