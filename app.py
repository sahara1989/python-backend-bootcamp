from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- Настройка БД SQLite ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Модель ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# --- HTML-маршруты (UI) ---
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

# --- API (JSON) ---
@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    tasks = Task.query.order_by(Task.id.asc()).all()
    # Преобразуем к простому JSON-формату
    data = [{"id": t.id, "content": t.content} for t in tasks]
    return jsonify(data), 200

@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    # Ожидаем JSON: { "task": "текст задачи" }
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

# --- Запуск локально; на Render помни про 0.0.0.0 и PORT ---
if __name__ == '__main__':
    # Локально можно так:
    app.run(debug=True)
    # На Render у тебя уже настроено:
    # import os
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host="0.0.0.0", port=port)