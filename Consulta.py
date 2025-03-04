import mysql.connector

# Conectar ao banco de dados
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Project1!",  # Altere para a sua senha
    database="meu_banco"    # Altere para o seu banco de dados
)

cursor = db.cursor()

# Consultar os dados da tabela usuarios
cursor.execute("SELECT * FROM usuarios")
users = cursor.fetchall()

# Exibir os dados no terminal
for user in users:
    print(user)

# Fechar a conexão
cursor.close()
db.close()