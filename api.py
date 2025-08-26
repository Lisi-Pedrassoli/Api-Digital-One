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

    cur.execute("""CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       email
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       password
                       TEXT
                       NOT
                       NULL,
                       name
                       TEXT
                   )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS posts
    (
        id
        INTEGER
        PRIMARY
        KEY
        AUTOINCREMENT,
        user_id
        INTEGER,
        description
        TEXT,
        FOREIGN
        KEY
                   (
        user_id
                   ) REFERENCES users
                   (
                       id
                   )
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

    # Validações básicas
    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    if len(password) < 6:
        return jsonify({"error": "A senha deve ter pelo menos 6 caracteres"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
                    (email, password, name))
        conn.commit()
        return jsonify({"message": "Usuário registrado com sucesso!"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email já cadastrado"}), 400
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    finally:
        conn.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify({
            "message": "Login realizado",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name']
            }
        })
    else:
        return jsonify({"error": "Email ou senha incorretos"}), 401


@app.route('/recover', methods=['POST'])
def recover():
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        return jsonify({"error": "Email e nova senha são obrigatórios"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "A nova senha deve ter pelo menos 6 caracteres"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cur.fetchone()

    if user:
        cur.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
        conn.commit()
        conn.close()
        return jsonify({"message": "Senha atualizada com sucesso!"})
    else:
        conn.close()
        return jsonify({"error": "Email não encontrado!"}), 404


@app.route('/update_name', methods=['POST'])
def update_name():
    data = request.json
    user_id = data.get('user_id')
    new_name = data.get('new_name')

    if not user_id or not new_name:
        return jsonify({"error": "ID do usuário e novo nome são obrigatórios"}), 400

    if not new_name.strip():
        return jsonify({"error": "O nome não pode estar vazio"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE users SET name=? WHERE id=?", (new_name.strip(), user_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Nome atualizado com sucesso!"})
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Erro ao atualizar nome: {str(e)}"}), 500


@app.route('/update_password', methods=['POST'])
def update_password():
    data = request.json
    user_id = data.get('user_id')
    new_password = data.get('new_password')

    if not user_id or not new_password:
        return jsonify({"error": "ID do usuário e nova senha são obrigatórios"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "A nova senha deve ter pelo menos 6 caracteres"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Senha atualizada com sucesso!"})
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Erro ao atualizar senha: {str(e)}"}), 500


@app.route("/post", methods=['POST'])
def create_post():
    data = request.json
    user_id = data.get('user_id')
    description = data.get('description')

    if not user_id or not description:
        return jsonify({"error": "ID do usuário e descrição são obrigatórios"}), 400

    if not description.strip():
        return jsonify({"error": "A descrição não pode estar vazia"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO posts (user_id, description) VALUES (?, ?)", (user_id, description.strip()))
        conn.commit()
        conn.close()
        return jsonify({"message": "Post criado com sucesso!"})
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Erro ao criar post: {str(e)}"}), 500


@app.route("/posts", methods=["GET"])
def list_posts():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
                    SELECT posts.id, posts.description, users.name, users.id as user_id
                    FROM posts
                             JOIN users ON posts.user_id = users.id
                    ORDER BY posts.id DESC
                    """)
        posts = cur.fetchall()
        conn.close()
        return jsonify([dict(p) for p in posts])
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Erro ao carregar posts: {str(e)}"}), 500


@app.route("/post/<int:post_id>", methods=["PUT"])
def edit_post(post_id):
    data = request.json
    user_id = data.get('user_id')
    description = data.get('description')

    if not user_id or not description:
        return jsonify({"error": "ID do usuário e descrição são obrigatórios"}), 400

    if not description.strip():
        return jsonify({"error": "A descrição não pode estar vazia"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM posts WHERE id=? AND user_id=?", (post_id, user_id))
        post = cur.fetchone()

        if post:
            cur.execute("UPDATE posts SET description=? WHERE id=?", (description.strip(), post_id))
            conn.commit()
            conn.close()
            return jsonify({"message": "Post atualizado com sucesso!"})
        else:
            conn.close()
            return jsonify({"error": "Você não pode editar esse post"}), 403
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Erro ao editar post: {str(e)}"}), 500


@app.route("/post/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "ID do usuário é obrigatório"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM posts WHERE id=? AND user_id=?", (post_id, user_id))
        post = cur.fetchone()

        if post:
            cur.execute("DELETE FROM posts WHERE id=?", (post_id,))
            conn.commit()
            conn.close()
            return jsonify({"message": "Post excluído com sucesso!"})
        else:
            conn.close()
            return jsonify({"error": "Você não pode excluir este post"}), 403
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Erro ao excluir post: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)