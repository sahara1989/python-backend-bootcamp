from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .models import Task, db  # импорт моделей и базы

# --- CSRF отключается для API ---
from . import csrf

# Создаём Blueprint для API
api_bp = Blueprint("api", __name__, url_prefix="/api")

# --- Все API‑маршруты начинаются с /api/ ---
@csrf.exempt
@api_bp.route("/tasks", methods=["GET"])
@login_required
def api_get_tasks():
    tasks = db.session.execute(
        db.select(Task).where(Task.user_id == current_user.id).order_by(Task.id.asc())
    ).scalars().all()
    return jsonify([{"id": t.id, "content": t.content} for t in tasks]), 200

@csrf.exempt
@api_bp.route("/tasks", methods=["POST"])
@login_required
def api_add_task():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
    payload = request.get_json(silent=True) or {}
    content = (payload.get("task") or "").strip()
    if not content:
        return jsonify({"error": "Field 'task' is required"}), 400
    if len(content) > 200:
        return jsonify({"error": "Task is too long (max 200 chars)"}), 422

    task = Task(content=content, user_id=current_user.id)
    db.session.add(task)
    db.session.commit()
    return jsonify({"id": task.id, "content": task.content}), 201

@csrf.exempt
@api_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def api_delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200
