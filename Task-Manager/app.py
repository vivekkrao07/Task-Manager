from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Allow frontend (index.html) to access backend APIs

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            category TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# 🟢 Add a new task
@app.route('/add-task', methods=['POST'])
def add_task():
    data = request.get_json()
    text = data.get('text')
    category = data.get('category')
    if not text or not category:
        return jsonify({"error": "Missing text or category"}), 400

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (text, category, completed) VALUES (?, ?, 0)', (text, category))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task added successfully!"})

# 📋 Get all tasks
@app.route('/get-tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, text, category, completed FROM tasks')
    tasks = cursor.fetchall()
    conn.close()

    task_list = [{"id": t[0], "text": t[1], "category": t[2], "completed": bool(t[3])} for t in tasks]
    return jsonify(task_list)

# ✅ Toggle task completion
@app.route('/toggle-complete/<int:task_id>', methods=['PATCH'])
def toggle_complete(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT completed FROM tasks WHERE id = ?', (task_id,))
    status = cursor.fetchone()
    if not status:
        return jsonify({"message": "Task not found"}), 404

    new_status = 0 if status[0] else 1
    cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task status updated"})

# 🗑️ Delete a task
@app.route('/delete-task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task deleted"})

# 🚀 Run the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
