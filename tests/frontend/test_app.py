import json
from unittest.mock import AsyncMock, Mock

import pytest
from frontend_service import message_handler


def test_index_returns_landing(client):
    resp = client.get("/")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Добро пожаловать в Microservices App" in text
    assert "/login" in text
    assert "/register" in text


@pytest.mark.asyncio
async def test_message_handler_acks_valid_message():
    msg = Mock()
    msg.data.decode.return_value = json.dumps({"username": "alice"})
    msg.ack = AsyncMock()
    await message_handler(msg)
    msg.ack.assert_awaited_once()


@pytest.mark.asyncio
async def test_message_handler_does_not_ack_on_invalid_json():
    msg = Mock()
    msg.data.decode.return_value = "not-json"
    msg.ack = AsyncMock()
    with pytest.raises(json.JSONDecodeError):
        await message_handler(msg)
    msg.ack.assert_not_awaited()
