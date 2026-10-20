import pytest
from flask_auth_service import db
from flask_auth_service.models import User, load_user
from sqlalchemy.exc import IntegrityError


def test_create_user(app):
    """Создание пользователя сохраняет запись в БД."""
    with app.app_context():
        user = User(username="alice", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        assert user.id is not None
        assert User.query.count() == 1


def test_username_is_unique(app):
    """Повторный username с одним значением unique нарушает целостность."""
    with app.app_context():
        first = User(username="bob", password_hash="h1")
        db.session.add(first)
        db.session.commit()

        second = User(username="bob", password_hash="h2")
        db.session.add(second)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_load_user_returns_user(app):
    """load_user должен вернуть пользователя по id."""
    with app.app_context():
        user = User(username="carol", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        assert load_user(user.id) == user


def test_load_user_missing_returns_none(app):
    """load_user с несуществующим id должен вернуть None."""
    with app.app_context():
        assert load_user(999_999) is None
