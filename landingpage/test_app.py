import os
import tempfile
import pytest
import sqlite3
from landingpage.app import create_app

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    app.config['WTF_CSRF_ENABLED'] = False

    # Substitui o caminho do banco de dados temporariamente
    original_connect = sqlite3.connect
    def temp_connect(path, *args, **kwargs):
        if path == "database.db":
            return original_connect(db_path, *args, **kwargs)
        return original_connect(path, *args, **kwargs)
    sqlite3.connect = temp_connect

    # Cria as tabelas diretamente no banco de teste
    with sqlite3.connect(db_path) as conn:
        # Tabela de respostas do formulário
        conn.execute("""
            CREATE TABLE IF NOT EXISTS respostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                sobrenome TEXT NOT NULL,
                email TEXT NOT NULL,
                telefone TEXT,
                cidade TEXT,
                uf TEXT,
                movimento TEXT,
                sindicato TEXT,
                categoria TEXT,
                empresa TEXT,
                estuda BOOLEAN,
                curso TEXT,
                instituicao TEXT,
                mensagem TEXT,
                imagem TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT email_format CHECK (email LIKE '%_@__%.__%')
            );
        """)
        
        # Tabela de usuários admin
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            );
        """)
        conn.commit()

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)
    sqlite3.connect = original_connect

def test_form_success(client):
    data = {
        'nome': 'Teste',
        'sobrenome': 'Unitario',
        'email': 'teste@unitario.com',
        'telefone': '(11) 91234-5678',
        'cidade': 'São Paulo',
        'uf': 'SP',
        'movimento': 'MTST',
        'sindicato': 'CUT',
        'categoria': 'serviços',
        'empresa': 'Empresa X',
        'estuda': 'sim',
        'curso': 'Engenharia',
        'instituicao': 'USP',
        'mensagem': 'Mensagem de teste'
    }
    response = client.post('/enviar', data=data)
    assert response.status_code == 200
    assert b'Resposta enviada com sucesso' in response.data

    # Verifica se o dado foi salvo no banco
    conn = sqlite3.connect(client.application.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM respostas WHERE email = ?", (data['email'],))
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == 'Teste'  # nome
    assert row[2] == 'Unitario'  # sobrenome
    assert row[3] == 'teste@unitario.com'  # email
    conn.close()

def test_form_validation_error(client):
    data = {
        'nome': '',  # Nome obrigatório
        'sobrenome': 'Unitario',
        'email': 'teste@unitario.com',
        'telefone': '(11) 91234-5678',
        'cidade': 'São Paulo',
        'uf': 'SP',
    }
    response = client.post('/enviar', data=data)
    assert response.status_code == 400
    assert b'Preencha todos os campos obrigat' in response.data 