import os
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_migrate import Migrate
from flask_wtf import CSRFProtect  # NEW
from flask_wtf.csrf import generate_csrf

app = Flask(__name__)

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# --- ключ сессии ---
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# --- (опционально) безопасные настройки cookie ---
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = True      # на Render (HTTPS)
app.config["REMEMBER_COOKIE_SECURE"] = True     # на Render (HTTPS)

# --- ИНИЦИАЛИЗАЦИЯ CSRF ---
csrf = CSRFProtect(app)  # NEW  ← включает защиту для всех HTML-форм (POST/PUT/DELETE)

# --- Конфигурация БД ---
db_url = os.environ.get("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if "sslmode=" not in db_url:
        sep = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{sep}sslmode=require"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "tasks.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- Flask-Login ---
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
@login_manager.unauthorized_handler
def unauthorized_callback():
    """
    Что делать, если неавторизованный пользователь попал на защищённый маршрут.
    Для API (/api/...) отдаём JSON 401. Для HTML — редиректим на /login.
    """
    # 1) Это API-запрос, если путь начинается с /api/
    is_api = request.path.startswith("/api/")

    # 2) Или клиент явно просит JSON (Accept: application/json)
    wants_json = request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]

    if is_api or wants_json:
        # Возвращаем JSON и статус 401 (Unauthorized)
        return jsonify({"error": "Unauthorized"}), 401

    # Для обычных HTML-страниц — редирект на /login, причём с сохранением next
    return redirect(url_for("login", next=request.path))


# --- Модели ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # удобная связь к задачам
    tasks = db.relationship("Task", backref="user", lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    # новый столбец (nullable=True, чтобы миграция прошла мягко для старых записей)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)

@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
from werkzeug.security import generate_password_hash, check_password_hash

# --- Регистрация ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Введите логин и пароль", "warning")
            return redirect(url_for("register"))

        # уникальность пользователя
        exists = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()
        if exists:
            flash("Пользователь уже существует", "danger")
            return redirect(url_for("register"))

        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash("Регистрация успешна! Теперь войдите.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# --- Логин ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Неверный логин или пароль", "danger")
            return redirect(url_for("login"))

        login_user(user)
        flash("Добро пожаловать!", "success")
        return redirect(url_for("index"))

    return render_template("login.html")

# --- Логаут ---
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("login"))

# --- Главная: список задач текущего пользователя ---
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        task_content = request.form.get("task", "").strip()
        if task_content:
            new_task = Task(content=task_content, user_id=current_user.id)
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for("index"))

    tasks = db.session.execute(
        db.select(Task).where(Task.user_id == current_user.id).order_by(Task.id.asc())
    ).scalars().all()

    return render_template("index.html", tasks=tasks)

# --- Удаление задачи текущего пользователя ---
@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    task = db.session.get(Task, id)
    if task and task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("index"))

# --- API (если хочешь тоже закрыть логином) ---


# Локальный запуск (на Render стартует gunicorn)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))