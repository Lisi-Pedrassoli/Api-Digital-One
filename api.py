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

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify({"message": "Login realizado","user": dict(user)})
    else:
        return jsonify({"error": "Email ou senha incorretos"}),401

@app.route('/recover', methods=['POST'])
def recover():
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cur.fetchone()

    if user:
        cur.execute("UPDATE users SET password=? WHERE email=?",(new_password, email))
        conn.commit()
        conn.close()
        return jsonify({"message": "Senha atualizada!"})
    else:
        conn.close()
        return jsonify({"error": "Email não encontrado!"}),404

@app.route('/update_name', methods=['POST'])
def update_name():
    data = request.json
    user_id = data.get('user_id')
    new_name = data.get('new_name')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET name=? WHERE id=?", (new_name, user_id))
    conn.commit()
    conn.close()

    return jsonify({"messege": "Nome atualizado!"})

@app.route('/update_password', methods=['POST'])
def update_password():
    data = request.json
    user_id = data.get('user_id')
    new_password = data.get('new_password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
    conn.commit()
    conn.close()

    return jsonify({"messege": "Senha atualizada!"})

@app.route("/post", methods=['POST'])
def create_post():
    data = request.json
    user_id = data.get('user_id')
    description = data.get('description')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO posts (user_id, description) VALUES (?, ?)",(user_id, description))
    conn.commit()
    conn.close()

    return jsonify({"messege": "Post criado com sucesso!"})

@app.route("/posts", methods=["GET"])
def list_posts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT posts.id, posts.description, users.name, users.id as user_id
    FROM posts JOIN users ON posts.user_id = users.id
    """)
    posts = cur.fetchall()
    conn.close()

    return jsonify([dict(p) for p in posts])

@app.route("/post/<int:post_id>", methods=["PUT"])
def edit_post(post_id):
    data = request.json
    user_id = data.get('user_id')
    description = data.get('description')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE id=? AND user_id=?", (post_id, user_id))
    post = cur.fetchone()

    if post:
        cur.execute("UPDATE posts SET description=? WHERE id=?", (description, post_id))
        conn.commit()
        conn.close()
        return jsonify({"messege": "Post atualizado!"})
    else:
        conn.close()
        return jsonify({"messege": "Você não pode editar esse post"}),403

@app.route("/post/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    data = request.json
    user_id = data.get('user_id')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE id=? AND user_id=?", (post_id, user_id))
    post = cur.fetchone()

    if post:
        cur.execute("DELETE FROM posts WHERE id=?", (post_id,))
        conn.commit()
        conn.close()
        return jsonify({"messege": "Post excluído!"})
    else:
        conn.close()
        return jsonify({"error": "Você não pode excluir este post"}),403

if __name__ == '__main__':
    app.run(debug=True)