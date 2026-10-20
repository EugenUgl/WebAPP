from unittest.mock import patch

from flask_auth_service.models import User


def _register(client, username, password):
    return client.post("/register", data={"username": username, "password": password})


def test_register_get_returns_form(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert "Регистрация" in resp.get_data(as_text=True)


@patch("flask_auth_service.routes.publish_user_registered")
def test_register_post_success_redirects_to_login(mock_publish, app, client):
    resp = _register(client, "alice", "secret")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    with app.app_context():
        user = User.query.filter_by(username="alice").first()
        assert user is not None
        assert user.password_hash != "secret"  # пароль хранится хешем
    mock_publish.assert_called_once_with("alice")


def test_register_duplicate_username_redirects_back(app, client):
    _register(client, "bob", "pass1")
    resp = _register(client, "bob", "pass2")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/register")

    with app.app_context():
        assert User.query.filter_by(username="bob").count() == 1


def test_register_does_not_publish_on_duplicate(app, client):
    _register(client, "carol", "pass1")
    with patch("flask_auth_service.routes.publish_user_registered") as mock_publish:
        _register(client, "carol", "pass2")
        mock_publish.assert_not_called()


def test_login_success_redirects_to_dashboard(app, client):
    _register(client, "dave", "pass")
    resp = client.post("/login", data={"username": "dave", "password": "pass"})
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/dashboard")


def test_login_wrong_password_returns_form_with_error(app, client):
    _register(client, "erin", "pass")
    resp = client.post("/login", data={"username": "erin", "password": "wrong"})
    assert resp.status_code == 200
    assert "Неверный логин или пароль" in resp.get_data(as_text=True)


def test_login_unknown_user_flashes_error(client):
    resp = client.post("/login", data={"username": "nobody", "password": "x"})
    assert resp.status_code == 200
    assert "Неверный логин или пароль" in resp.get_data(as_text=True)


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_dashboard_accessible_after_login(app, client):
    _register(client, "frank", "pass")
    client.post("/login", data={"username": "frank", "password": "pass"})
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert "frank" in resp.get_data(as_text=True)


def test_logout_clears_session(app, client):
    _register(client, "grace", "pass")
    client.post("/login", data={"username": "grace", "password": "pass"})
    assert client.get("/dashboard").status_code == 200

    resp = client.get("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    # После выхода /dashboard снова закрыт
    assert client.get("/dashboard").status_code == 302
