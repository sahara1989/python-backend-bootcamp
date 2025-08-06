from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .models import db, User, Task
from .forms import RegisterForm, LoginForm  # подключаем формы
from .forms import TaskForm
from flask_dance.contrib.github import github
from flask import current_app as app



main_bp = Blueprint("main", __name__)

# === Регистрация ===
@main_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()

        exists = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()
        if exists:
            flash("Пользователь уже существует", "danger")
            return redirect(url_for("main.register"))

        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash("Регистрация успешна! Теперь войдите.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)

# === Логин ===
@main_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()

        user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Неверный логин или пароль", "danger")
            return redirect(url_for("main.login"))

        login_user(user)
        flash("Добро пожаловать!", "success")
        return redirect(url_for("main.index"))

    return render_template("login.html", form=form)

# === Выход ===
@main_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("main.login"))

# === Главная (список задач + добавление) ===
@main_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = TaskForm()

    if form.validate_on_submit():
        task_content = form.task.data.strip()
        new_task = Task(content=task_content, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("main.index"))

    tasks = db.session.execute(
        db.select(Task).where(Task.user_id == current_user.id).order_by(Task.id.asc())
    ).scalars().all()

    return render_template("index.html", tasks=tasks, form=form)

# === Удаление задачи ===
@main_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    task = db.session.get(Task, id)
    if task and task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("main.index"))

@main_bp.route("/login/github")
def github_login():
    # если пользователь ещё не авторизовался через GitHub — перенаправим его
    if not github.authorized:
        return redirect(url_for("github.login"))

    # пробуем получить информацию о пользователе от GitHub
    resp = github.get("/user")
    if not resp.ok:
        flash("Ошибка при получении данных от GitHub", "danger")
        return redirect(url_for("main.login"))

    # парсим ответ GitHub
    github_info = resp.json()
    github_id = str(github_info["id"])
    username = github_info.get("login", f"user_{github_id}")

    # проверяем, есть ли такой пользователь в нашей базе
    user = db.session.execute(
        db.select(User).filter_by(github_id=github_id)
    ).scalar_one_or_none()

    # если нет — регистрируем нового
    if not user:
        user = User(username=username, github_id=github_id)
        db.session.add(user)
        db.session.commit()

    # логиним пользователя
    login_user(user)
    flash("Успешный вход через GitHub", "success")
    return redirect(url_for("main.index"))

