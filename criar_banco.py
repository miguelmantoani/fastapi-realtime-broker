import sqlite3

# Conecta (ou cria) o banco de dados 'messages.db'
conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

# Cria a tabela messages se ela não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
''')

# Salva (commit) as alterações
conn.commit()

print("Banco e tabela criados com sucesso!")

# Fecha a conexão
conn.close()
