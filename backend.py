from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import mysql.connector

app = Flask(__name__, template_folder="templates")
CORS(app)

# Conexão com o banco de dados
def get_db_connection():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Project1!",
        database="meu_banco"
    )
    return db


db = get_db_connection()
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100),
    telefone VARCHAR(20),
    cpf VARCHAR(14),
    curso_id INT,
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
)
""")
db.commit()

# Rota para a página inicial
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT * FROM cursos")  
    cursos = cursor.fetchall()
    conn.close()
    return render_template('frontend.html', cursos=cursos)

# Rota para listar cursos
@app.route('/cursos', methods=['GET'])
def get_cursos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT * FROM cursos") 
    cursos = cursor.fetchall()
    cursos_list = [{"id": c[0], "nome": c[1]} for c in cursos]
    conn.close()
    return jsonify(cursos_list)

# Rota para listar usuários
@app.route('/usuarios', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT u.id, u.nome, u.email, u.telefone, u.cpf, c.nome AS curso FROM usuarios u LEFT JOIN cursos c ON u.curso_id = c.id")
    users = cursor.fetchall()
    users_list = [{"id": u[0], "nome": u[1], "email": u[2], "telefone": u[3], "cpf": u[4], "curso": u[5]} for u in users]
    conn.close()
    return render_template('banco.html', users=users_list)

# Rota para adicionar um usuário
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    if not all(key in data for key in ("nome", "email", "telefone", "cpf", "curso_id")):
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, telefone, cpf, curso_id) VALUES (%s, %s, %s, %s, %s)",
                       (data['nome'], data['email'], data['telefone'], data['cpf'], data['curso_id']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Usuário adicionado com sucesso!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    
# Rota para remover um usuário
@app.route('/remover/<int:id>', methods=['POST'])
def remove_user(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/usuarios')
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

# Iniciar o servidor
if __name__ == '__main__':
    app.run(debug=True)
