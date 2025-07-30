import os
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_url = os.environ.get("DATABASE_URL")

if db_url:
    # 1) postgres:// -> postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    # 2) принудительно использовать psycopg (v3)
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    # 3) добавить sslmode=require, если его нет
    if "sslmode=" not in db_url:
        sep = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{sep}sslmode=require"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "tasks.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ----- Модель -----
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

# Создаём таблицы при старте приложения
with app.app_context():
    db.create_all()

# ----- HTML-маршруты -----
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_content = request.form.get('task', '').strip()
        if task_content:
            new_task = Task(content=task_content)
            db.session.add(new_task)
            db.session.commit()
        return redirect('/')

    tasks = Task.query.order_by(Task.id.asc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

# ----- API -----
@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    tasks = Task.query.order_by(Task.id.asc()).all()
    return jsonify([{"id": t.id, "content": t.content} for t in tasks]), 200

@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
    payload = request.get_json(silent=True) or {}
    content = (payload.get("task") or "").strip()
    if not content:
        return jsonify({"error": "Field 'task' is required"}), 400
    if len(content) > 200:
        return jsonify({"error": "Task is too long (max 200 chars)"}), 422

    task = Task(content=content)
    db.session.add(task)
    db.session.commit()
    return jsonify({"id": task.id, "content": task.content}), 201

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200

# ----- Локальный запуск (Gunicorn на Render сам импортирует app) -----
if __name__ == "__main__":
    # локально можно так
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))