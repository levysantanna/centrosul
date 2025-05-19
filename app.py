
from flask import Flask, request, redirect, render_template
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS respostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT,
                telefone TEXT,
                mensagem TEXT,
                imagem TEXT
            );
        """)

@app.route('/')
def formulario():
    return render_template('form.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form.get('telefone', '')
    mensagem = request.form.get('mensagem', '')

    imagem = request.files.get('imagem')
    imagem_path = ''
    if imagem and imagem.filename != '':
        filename = secure_filename(imagem.filename)
        imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        imagem.save(imagem_path)

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO respostas (nome, email, telefone, mensagem, imagem)
            VALUES (?, ?, ?, ?, ?);
        """, (nome, email, telefone, mensagem, imagem_path))
        conn.commit()

    return "Resposta enviada com sucesso!"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
