import asyncio
import json
import logging

import nats

logger = logging.getLogger(__name__)

NATS_URL = "nats://nats:4222"
STREAM_NAME = "USER_EVENTS"
SUBJECT = "user.registered"


async def _publish_message(username: str):
    # Подключаемся к NATS
    nc = await nats.connect(NATS_URL)
    js = nc.jetstream()

    # Создаем поток (Stream), если его еще нет
    try:
        await js.add_stream(name=STREAM_NAME, subjects=[SUBJECT])
    except Exception:
        pass  # Если поток уже есть, игнорируем ошибку

    # Формируем сообщение и публикуем его в JetStream
    payload = {"username": username}
    ack = await js.publish(SUBJECT, json.dumps(payload).encode())
    logger.info("Событие отправлено в NATS. Sequence: %s", ack.seq)

    # Закрываем соединение
    await nc.close()


def publish_user_registered(username: str):
    """Синхронная обертка для вызова из Flask"""
    try:
        # Запускаем асинхронную функцию из синхронного кода Flask
        asyncio.run(_publish_message(username))
    except Exception as e:
        logger.error("Ошибка при отправке события в NATS: %s", e)
