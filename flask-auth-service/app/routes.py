# app/routes.py
from flask import Blueprint, flash, redirect, render_template_string, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .events import publish_user_registered  # <-- Импорт нашей функции
from .models import User

auth = Blueprint("auth", __name__)

# --- HTML-шаблоны ---

HTML_REGISTER = """
<!DOCTYPE html>
<html>
<head><title>Регистрация</title></head>
<body style="font-family: Arial, sans-serif; margin: 40px;">
    <h2>Регистрация нового пользователя</h2>
    {% with messages = get_flashed_messages() %}
      {% if messages %}{% for msg in messages %}<p style="color: red;">{{ msg }}</p>{% endfor %}{% endif %}
    {% endwith %}
    <form method="POST">
        <input type="text" name="username" placeholder="Логин" required><br><br>
        <input type="password" name="password" placeholder="Пароль" required><br><br>
        <button type="submit">Зарегистрироваться</button>
    </form>
    <p>Уже есть аккаунт? <a href="{{ url_for('auth.login') }}">Войти</a></p>
</body>
</html>
"""

HTML_LOGIN = """
<!DOCTYPE html>
<html>
<head><title>Вход</title></head>
<body style="font-family: Arial, sans-serif; margin: 40px;">
    <h2>Вход в аккаунт</h2>
    {% with messages = get_flashed_messages() %}
      {% if messages %}{% for msg in messages %}<p style="color: red;">{{ msg }}</p>{% endfor %}{% endif %}
    {% endwith %}
    <form method="POST">
        <input type="text" name="username" placeholder="Логин" required><br><br>
        <input type="password" name="password" placeholder="Пароль" required><br><br>
        <button type="submit">Войти</button>
    </form>
    <p>Еще нет аккаунта? <a href="{{ url_for('auth.register') }}">Зарегистрироваться</a></p>
</body>
</html>
"""

HTML_DASHBOARD = """
<!DOCTYPE html>
<html>
<head><title>Личный кабинет</title></head>
<body style="font-family: Arial, sans-serif; margin: 40px;">
    <h2>Личный кабинет микросервиса</h2>
    <p>Привет, <strong>{{ current_user.username }}</strong>!</p>
    <p>Вы успешно авторизованы в Docker-контейнере.</p>
    <a href="{{ url_for('auth.logout') }}">Выйти из аккаунта</a>
</body>
</html>
"""

# --- Маршруты ---


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Этот логин уже занят!")
            return redirect(url_for("auth.register"))

        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        # Отправляем событие в NATS
        publish_user_registered(new_user.username)

        flash("Регистрация успешна! Войдите.")
        return redirect(url_for("auth.login"))

    return render_template_string(HTML_REGISTER)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("auth.dashboard"))
        flash("Неверный логин или пароль!")

    return render_template_string(HTML_LOGIN)


@auth.route("/dashboard")
@login_required
def dashboard():
    return render_template_string(HTML_DASHBOARD)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
