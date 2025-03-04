from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import mysql.connector

app = Flask(__name__, template_folder="templates")  
CORS(app)  

# Conexão com o banco de dados
def get_db_connection():
    # Recria a conexão com o banco de dados sempre que for chamada
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Project1!",
        database="meu_banco"
    )
    return db

# Criar tabela se não existir
db = get_db_connection()
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100),
    telefone VARCHAR(20),
    cpf VARCHAR(14)
)
""")
db.commit()

# **ROTA PRINCIPAL**
@app.route('/')
def home():
    return render_template("Frontend.html")  # Exibe a página inicial

# **listar usuários**
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    users = cursor.fetchall()
    users_list = [{"id": u[0], "nome": u[1], "email": u[2], "telefone": u[3], "cpf": u[4]} for u in users]
    conn.close()
    return jsonify(users_list)

# **Remover usuários**
@app.route('/remover/<int:id>', methods=['POST'])
def remover_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('usuarios'))

# **inserir um usuário**
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    if not all(key in data for key in ("nome", "email", "telefone", "cpf")):
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, telefone, cpf) VALUES (%s, %s, %s, %s)",
                       (data['nome'], data['email'], data['telefone'], data['cpf']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Usuário adicionado com sucesso!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

# **exibir a lista de usuários**
@app.route('/usuarios')
def usuarios():
    return render_template("Banco.html")

# **Iniciar o servidor**
if __name__ == '__main__':
    # Certifique-se de rodar o arquivo Backend.py
    app.run(debug=True)
