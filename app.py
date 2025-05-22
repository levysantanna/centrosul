import logging
from flask import Flask, request, redirect, render_template, jsonify
import sqlite3, os
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect
import re
from datetime import datetime


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    app.logger.info('Application started')

    # CSRF error handler
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        app.logger.warning(f"CSRF error: {e.description}")
        return jsonify({"error": "Erro de validação CSRF"}), 403

    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Configuração de segurança
    csrf = CSRFProtect(app)
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def sanitize_input(text):
        if not text:
            return ""
        # Remove caracteres especiais e limita o tamanho
        text = re.sub(r'[<>]', '', text)
        return text[:500]  # Limita a 500 caracteres

    def init_db():
        with sqlite3.connect("database.db") as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS respostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    sobrenome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    telefone TEXT NOT NULL,
                    cidade TEXT NOT NULL,
                    uf TEXT NOT NULL,
                    movimento TEXT,
                    sindicato TEXT,
                    area_tecnologia TEXT,
                    empresa TEXT,
                    estuda BOOLEAN,
                    curso TEXT,
                    instituicao TEXT,
                    mensagem TEXT,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT email_format CHECK (email LIKE '%_@__%.__%')
                );
            """)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/enviar', methods=['POST'])
    @limiter.limit("5 per minute")
    def handle_enviar():
        try:
            # Validação de CSRF
            # if not csrf.validate():
            #     app.logger.warning(f"CSRF validation failed from IP: {request.remote_addr}")
            #     return jsonify({"error": "Erro de validação CSRF"}), 403
            # Sanitização e validação dos inputs
            nome = sanitize_input(request.form.get('nome', ''))
            sobrenome = sanitize_input(request.form.get('sobrenome', ''))
            email = sanitize_input(request.form.get('email', ''))
            telefone = sanitize_input(request.form.get('telefone', ''))
            cidade = sanitize_input(request.form.get('cidade', ''))
            uf = sanitize_input(request.form.get('uf', ''))
            movimento = sanitize_input(request.form.get('movimento', ''))
            sindicato = sanitize_input(request.form.get('sindicato', ''))
            area_tecnologia = sanitize_input(request.form.get('area_tecnologia', ''))
            empresa = sanitize_input(request.form.get('empresa', ''))
            estuda = request.form.get('estuda') == 'sim'
            curso = sanitize_input(request.form.get('curso', ''))
            instituicao = sanitize_input(request.form.get('instituicao', ''))
            mensagem = sanitize_input(request.form.get('mensagem', ''))

            if not nome or not sobrenome or not email or not telefone:
                app.logger.warning("Campos obrigatórios ausentes: nome, sobrenome, email, telefone. IP: %s", request.remote_addr)
                return jsonify({"error": "Preencha todos os campos obrigatórios: nome, sobrenome, email e telefone."}), 400

            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                app.logger.warning("Email inválido: %s IP: %s", email, request.remote_addr)
                return jsonify({"error": "Email inválido"}), 400

            if not telefone.isdigit() or len(telefone) != 11:
                app.logger.warning("Telefone inválido: %s IP: %s", telefone, request.remote_addr)
                return jsonify({"error": "Telefone deve conter 11 dígitos (DDD+telefone)"}), 400

            # imagem = request.files.get('imagem')
            # imagem_path = ''
            # if imagem and imagem.filename != '':
            #     if not allowed_file(imagem.filename):
            #         return jsonify({"error": "Tipo de arquivo não permitido"}), 400
                
            #     filename = secure_filename(imagem.filename)
            #     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            #     filename = f"{timestamp}_{filename}"
            #     imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #     imagem.save(imagem_path)

            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO respostas (
                        nome, sobrenome, email, telefone, cidade, uf,
                        movimento, sindicato, area_tecnologia, empresa,
                        estuda, curso, instituicao, mensagem, ip_address
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    nome, sobrenome, email, telefone, cidade, uf,
                    movimento, sindicato, area_tecnologia, empresa,
                    estuda, curso, instituicao, mensagem, request.remote_addr
                ))
                conn.commit()
                app.logger.info('Resposta enviada com sucesso!')
            return jsonify({"message": "Resposta enviada com sucesso!"}), 200

        except (sqlite3.Error, ValueError) as e:
            app.logger.error("Erro ao processar a requisição: %s", str(e))
            return jsonify({"error": "Erro ao processar a requisição"}), 500
        except Exception as e:
            app.logger.error("Erro inesperado: %s", str(e))
            return jsonify({"error": "Erro inesperado ao processar a requisição"}), 500

    # Inicializa o banco de dados quando a aplicação é criada
    init_db()
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
