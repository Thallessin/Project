from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Permite conexão entre frontend e backend

# **ROTA PRINCIPAL**
@app.route('/')
def home():
    return jsonify({"message": "Servidor Flask rodando com sucesso!"})

# Conectar ao banco de dados
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Project1!",
        database="meu_banco"
    )
    cursor = db.cursor()
except mysql.connector.Error as err:
    print(f"Erro ao conectar ao MySQL: {err}")
    exit(1)

# Criar tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100),
    telefone VARCHAR(20),
    cpf VARCHAR(20)
)
""")
db.commit()

# Rota para inserir um usuário
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    if 'nome' not in data or 'email' not in data or 'telefone' not in data or 'cpf' not in data:
        return jsonify({"error": "Os campos 'nome', 'email', 'telefone' e 'cpf' são obrigatórios"}), 400
    
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, telefone, cpf) VALUES (%s, %s, %s, %s)",
            (data['nome'], data['email'], data['telefone'], data['cpf'])
        )
        db.commit()
        return jsonify({"message": "Usuário adicionado com sucesso!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

# Rota para listar usuários
@app.route('/users', methods=['GET'])
def get_users():
    cursor.execute("SELECT * FROM usuarios")
    users = cursor.fetchall()
    return jsonify(users)

# Iniciar o servidor
if __name__ == '__main__':
    app.run(debug=True)