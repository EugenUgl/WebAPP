import importlib.util
import os
import sys
from pathlib import Path

import pytest

# Отключаем запуск фонового слушателя NATS ДО загрузки модуля app.py —
# иначе демон-поток будет пытаться подключиться к брокеру при импорте.
os.environ["TESTING"] = "1"

FE_DIR = Path(__file__).resolve().parents[2] / "frontend-service"
PKG = "frontend_service"


# Импорт модулей вручную (каталог содержит дефис)
def _load(fullname: str, path: Path):
    spec = importlib.util.spec_from_file_location(fullname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[fullname] = mod
    spec.loader.exec_module(mod)
    return mod


# Загружаем корневой модуль, чтобы контекст "frontend-service" лежал в sys.modules
_load("frontend_service", FE_DIR / "app.py")


@pytest.fixture()
def client():
    from frontend_service import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
