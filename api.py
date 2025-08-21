from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             email TEXT UNIQUE NOT NULL,
             password TEXT NOT NULL,
             name TEXT
             )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                description TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
                )""")

    conn.commit()
    conn.close()

init_db()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
                    (email, password, name))
        conn.commit()
        return jsonify({"message": "Usuário registrado com sucesso!"})
    except:
        return jsonify({"error": "Email já cadastrado"}), 400
    finally:
        conn.close()