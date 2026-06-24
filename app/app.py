from flask import Flask, jsonify, request
import os
import psycopg2
from datetime import datetime

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'tododb'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'password')
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': str(datetime.now())})

@app.route('/todos', methods=['GET'])
def get_todos():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, title, done, created_at FROM todos ORDER BY created_at DESC')
    todos = [{'id': r[0], 'title': r[1], 'done': r[2], 'created_at': str(r[3])} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(todos)

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO todos (title) VALUES (%s) RETURNING id', (data['title'],))
    todo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'id': todo_id, 'title': data['title'], 'done': False}), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE todos SET done = %s WHERE id = %s', (data['done'], todo_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Updated'})

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM todos WHERE id = %s', (todo_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Deleted'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)