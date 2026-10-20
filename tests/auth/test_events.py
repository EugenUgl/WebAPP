from unittest.mock import patch

from flask_auth_service import events


@patch("flask_auth_service.events._publish_message")
def test_publish_user_registered_delegates_to_async(mock_async):
    """Синхронная обертка вызывает асинхронную функцию с тем же username."""
    events.publish_user_registered("alice")
    mock_async.assert_called_once_with("alice")


@patch("flask_auth_service.events._publish_message", side_effect=Exception("nats down"))
def test_publish_user_registered_swallows_errors(mock_async):
    """Сбой NATS не должен прерывать регистрацию (ошибка логируется)."""
    # Не должно бросать исключение наружу
    events.publish_user_registered("alice")
