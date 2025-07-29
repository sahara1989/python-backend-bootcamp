from flask import Flask, render_template, request, redirect, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    tasks = load_tasks()
    if request.method == 'POST':
        task = request.form['task']
        if task:
            tasks.append(task)
            save_tasks(tasks)
        return redirect('/')
    return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)
    return redirect('/')

# -----------------------
# ✅ API
# -----------------------

@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json()
    if not data or 'task' not in data:
        return jsonify({'error': 'No task provided'}), 400

    tasks = load_tasks()
    tasks.append(data['task'])
    save_tasks(tasks)
    return jsonify({'message': 'Task added'}), 201

@app.route('/api/tasks/<int:index>', methods=['DELETE'])
def api_delete_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)
        return jsonify({'message': 'Task deleted'}), 200
    return jsonify({'error': 'Invalid index'}), 404

if __name__ == '__main__':
    app.run(debug=True)