import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    # База данных будет сохраняться внутри контейнера (или подключенного тома).
    # В тестах задаётся через DATABASE_URL (например, sqlite:////tmp/test.db).
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///microservice_users.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Регистрируем маршруты (Blueprint)
    from .routes import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    with app.app_context():
        db.create_all()

    return app
