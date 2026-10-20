import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Каталог сервиса содержит дефис ("flask-auth-service"), поэтому его нельзя
# импортировать обычным способом. Загружаем модули вручную под псевдонимом.
AUTH_DIR = Path(__file__).resolve().parents[2] / "flask-auth-service"
APP_DIR = AUTH_DIR / "app"
PKG = "flask_auth_service"


def _load(fullname: str, path: Path):
    spec = importlib.util.spec_from_file_location(fullname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[fullname] = mod
    spec.loader.exec_module(mod)
    return mod


# Сначала пакет (__init__.py), чтобы относительные импорты (.models и т.п.)
# резолвились через __path__.
_pkg = _load(PKG, APP_DIR / "__init__.py")
_pkg.__path__ = [str(APP_DIR)]
_load(f"{PKG}.models", APP_DIR / "models.py")
_load(f"{PKG}.events", APP_DIR / "events.py")
_load(f"{PKG}.routes", APP_DIR / "routes.py")


@pytest.fixture()
def app(tmp_path, monkeypatch):
    # Изолированная тестовая БД в tmp_path + TESTING для Flask-Login
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    from flask_auth_service import create_app

    application = create_app()
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    yield application


@pytest.fixture()
def client(app):
    # Публикацию события в NATS мокаем глобально: юнит-тесты не должны
    # подключаться к реальному брокеру. Отдельные тесты могут переопределять
    # поведение через @patch на конкретный вызов.
    with patch("flask_auth_service.routes.publish_user_registered") as mock_publish:
        with app.test_client() as c:
            c.mock_publish = mock_publish
            yield c
