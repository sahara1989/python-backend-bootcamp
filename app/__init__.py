import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from .config import DevelopmentConfig, ProductionConfig

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app():

    app = Flask(__name__)

    # 1. Определяем окружение (по умолчанию development)
    env = os.environ.get("FLASK_ENV", "development").lower()

    # 2. Подключаем конфигурацию из config.py
    if env == "production":
        app.config.from_object(ProductionConfig())
    else:
        app.config.from_object(DevelopmentConfig())

    # 3. Инициализация расширений
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    # важно, чтобы БД знала о моделях
    from .models import User  
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))



    # 4. Регистрация blueprint'ов
    from .routes import main_bp
    from .api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Обработка ошибок
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500

    return app

