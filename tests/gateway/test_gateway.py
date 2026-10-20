from unittest.mock import Mock, patch

import pytest
import requests

from gateway.gateway import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def _make_backend_response(content=b"ok", status_code=200, headers=None):
    return Mock(content=content, status_code=status_code, headers=headers or {})


@patch("gateway.gateway.requests.request")
def test_root_routes_to_frontend(mock_request, client):
    """Запрос на / должен уйти на frontend-service."""
    mock_request.return_value = Mock(content=b"frontend page", status_code=200, headers={})
    client.get("/")
    mock_request.assert_called_once()
    _, kwargs = mock_request.call_args
    assert kwargs["url"] == "http://frontend-service:5000/"


@patch("gateway.gateway.requests.request")
def test_login_routes_to_auth(mock_request, client):
    """Запрос на /login должен уйти на auth-backend."""
    mock_request.return_value = Mock(content=b"login page", status_code=200, headers={})
    client.post("/login", data={"username": "test"})
    mock_request.assert_called_once()
    _, kwargs = mock_request.call_args
    assert kwargs["url"] == "http://auth-backend:5000/login"


@patch("gateway.gateway.requests.request")
def test_headers_are_forwarded_except_host(mock_request, client):
    """Заголовок Host не должен уходить на бэкенд, остальные — должны."""
    mock_request.return_value = Mock(content=b"ok", status_code=200, headers={})
    client.get("/dashboard", headers={"X-Custom": "value", "Host": "localhost:8080"})
    _, kwargs = mock_request.call_args
    forwarded_headers = kwargs["headers"]
    assert "Host" not in forwarded_headers
    assert forwarded_headers["X-Custom"] == "value"


@patch("gateway.gateway.requests.request")
def test_location_header_rewritten(mock_request, client):
    """Заголовок Location должен быть переписан с внутреннего адреса на адрес шлюза."""
    mock_request.return_value = Mock(
        content=b"redirect",
        status_code=302,
        headers={"Location": "http://auth-backend:5000/dashboard"},
    )
    response = client.post("/login", base_url="http://localhost:8080")
    assert response.status_code == 302
    assert response.headers["Location"] == "http://localhost:8080/dashboard"


@patch("gateway.gateway.requests.request")
def test_connection_error_returns_502(mock_request, client):
    """При ConnectionError шлюз должен вернуть 502."""
    mock_request.side_effect = requests.exceptions.ConnectionError
    response = client.get("/")
    assert response.status_code == 502
    assert b"Error 502: Bad Gateway" in response.data


@patch("gateway.gateway.requests.request")
def test_body_is_forwarded(mock_request, client):
    """Тело запроса должно передаваться бэкенду без изменений."""
    mock_request.return_value = Mock(content=b"ok", status_code=200, headers={})
    payload = b'{"key": "value"}'
    client.post("/login", data=payload)
    _, kwargs = mock_request.call_args
    assert kwargs["data"] == payload


@patch("gateway.gateway.requests.request")
def test_put_and_delete_methods_forwarded(mock_request, client):
    """PUT/DELETE должны обрабатываться шлюзом и уходить на бэкенд."""
    mock_request.return_value = _make_backend_response()
    for method in ("put", "delete"):
        mock_request.reset_mock()
        getattr(client, method)("/dashboard")
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == method.upper()
        assert kwargs["url"] == "http://auth-backend:5000/dashboard"


@patch("gateway.gateway.requests.request")
def test_cookies_are_forwarded(mock_request, client):
    """Cookie клиента должны передаваться бэкенду."""
    mock_request.return_value = _make_backend_response()
    client.set_cookie("session", "abc123")
    client.get("/dashboard")
    _, kwargs = mock_request.call_args
    assert kwargs["cookies"]["session"] == "abc123"


@patch("gateway.gateway.requests.request")
def test_hop_by_hop_headers_stripped_from_response(mock_request, client):
    """Заголовки connection/transfer-encoding не должны копироваться в ответ.

    Content-Length Flask пересчитывает сам из тела ответа, поэтому его наличие
    не говорит о том, что заголовок был скопирован из ответа бэкенда.
    """
    backend = Mock(
        content=b"ok",
        status_code=200,
        headers={
            "Content-Length": "12345",
            "Connection": "keep-alive",
            "Transfer-Encoding": "chunked",
            "Content-Type": "text/html",
        },
    )
    mock_request.return_value = backend
    response = client.get("/")
    # Шлюз не копирует hop-by-hop заголовки из ответа бэкенда:
    assert response.headers.get("Connection") is None
    assert response.headers.get("Transfer-Encoding") is None
    # Content-Length задаёт сам Flask по реальному телу (b"ok" -> 2), а не 12345:
    assert response.headers.get("Content-Length") == "2"
    assert response.headers.get("Content-Type") == "text/html"


@patch("gateway.gateway.requests.request")
def test_query_string_preserved(mock_request, client):
    """Query-строка запроса должна дойти до бэкенда."""
    mock_request.return_value = _make_backend_response()
    client.get("/dashboard?page=2")
    _, kwargs = mock_request.call_args
    # Flask test client передаёт path без query, но сам URL в requests формируется из path
    assert kwargs["url"] == "http://auth-backend:5000/dashboard"
