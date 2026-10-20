import pytest
import requests
from unittest.mock import patch, Mock
from gateway.gateway import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("gateway.gateway.requests.request")
def test_root_routes_to_frontend(mock_request, client):
    """Запрос на / должен уйти на frontend-service."""
    mock_request.return_value = Mock(
        content=b"frontend page",
        status_code=200,
        headers={}
    )
    client.get("/")
    mock_request.assert_called_once()
    _, kwargs = mock_request.call_args
    assert kwargs["url"] == "http://frontend-service:5000/"


@patch("gateway.gateway.requests.request")
def test_login_routes_to_auth(mock_request, client):
    """Запрос на /login должен уйти на auth-backend."""
    mock_request.return_value = Mock(
        content=b"login page",
        status_code=200,
        headers={}
    )
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
        headers={"Location": "http://auth-backend:5000/dashboard"}
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