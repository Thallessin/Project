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

# Inicializar o banco de dados
db = get_db_connection()
cursor = db.cursor()

# Criar tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    curso_id INT,
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
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
    turma_id INT,
    FOREIGN KEY (curso_id) REFERENCES cursos(id),
    FOREIGN KEY (turma_id) REFERENCES turmas(id)
)
""")
db.commit()

# Página inicial - Cadastro de Alunos
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT * FROM cursos")  
    cursos = cursor.fetchall()
    conn.close()
    return render_template('frontend.html', cursos=cursos)

# API para listar cursos
@app.route('/cursos', methods=['GET'])
def get_cursos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT * FROM cursos") 
    cursos = cursor.fetchall()
    cursos_list = [{"id": c[0], "nome": c[1]} for c in cursos]
    conn.close()
    return jsonify(cursos_list)

# Página para listar todas as turmas
@app.route('/usuarios', methods=['GET'])
def listar_turmas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM turmas")
    turmas = cursor.fetchall()
    turmas_list = [{"id": t[0], "nome": t[1]} for t in turmas]
    conn.close()
    return render_template('banco.html', turmas=turmas_list)

# Página para listar alunos de uma turma
@app.route('/turma/<int:turma_id>', methods=['GET'])
def listar_alunos_da_turma(turma_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.nome, u.email, u.telefone, u.cpf
        FROM usuarios u
        WHERE u.turma_id = %s
    """, (turma_id,))
    alunos = cursor.fetchall()

    cursor.execute("SELECT nome FROM turmas WHERE id = %s", (turma_id,))
    turma_nome = cursor.fetchone()
    turma_nome = turma_nome[0] if turma_nome else "Turma Não Encontrada"

    alunos_list = [{"id": a[0], "nome": a[1], "email": a[2], "telefone": a[3], "cpf": a[4]} for a in alunos]
    conn.close()
    return render_template('turma.html', alunos=alunos_list, turma_nome=turma_nome)

# Função para encontrar ou criar turma baseado no curso
def encontrar_ou_criar_turma(curso_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT nome FROM cursos WHERE id = %s", (curso_id,))
    curso_nome = cursor.fetchone()
    if not curso_nome:
        conn.close()
        raise ValueError("Curso não encontrado")

    nome_turma = f"Turma {curso_nome[0]}"

    cursor.execute("SELECT id FROM turmas WHERE nome = %s AND curso_id = %s", (nome_turma, curso_id))
    turma = cursor.fetchone()

    if turma:
        turma_id = turma[0]
    else:
        cursor.execute("INSERT INTO turmas (nome, curso_id) VALUES (%s, %s)", (nome_turma, curso_id))
        conn.commit()
        turma_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return turma_id

# API para adicionar aluno
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    if not all(key in data for key in ("nome", "email", "telefone", "cpf", "curso_id")):
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400

    try:
        turma_id = encontrar_ou_criar_turma(data['curso_id'])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nome, email, telefone, cpf, curso_id, turma_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['nome'], data['email'], data['telefone'], data['cpf'], data['curso_id'], turma_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Usuário adicionado com sucesso!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

# API para remover aluno
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

# Rodar servidor
if __name__ == '__main__':
    app.run(debug=True)