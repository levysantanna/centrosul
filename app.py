from flask import Flask, request, redirect, render_template, jsonify, session, flash, url_for
import sqlite3, os
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import re
from datetime import datetime
import logging
import bcrypt
from functools import wraps

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-padrao-mudar-em-producao')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    # Configuração de segurança
    csrf = CSRFProtect(app)
    
    # Configuração do Rate Limiter com suporte a Redis
    limiter_storage_uri = os.environ.get('REDIS_URL', 'memory://')
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=limiter_storage_uri
    )
    
    # Log da configuração do rate limiter
    if limiter_storage_uri.startswith('redis://'):
        logger.info(f"Rate limiter configurado com Redis: {limiter_storage_uri}")
    else:
        logger.info("Rate limiter configurado com storage em memória (desenvolvimento)")
        if os.environ.get('FLASK_ENV') == 'production':
            logger.warning("AVISO: Usando storage em memória em produção. Configure REDIS_URL para melhor performance.")

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def sanitize_input(text):
        if not text:
            return ""
        # Remove caracteres especiais e limita o tamanho
        text = re.sub(r'[<>]', '', text)
        return text[:500]  # Limita a 500 caracteres

    def hash_password(password):
        """Hash da senha usando bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(password, hashed):
        """Verifica a senha contra o hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    def admin_required(f):
        """Decorator para proteger rotas admin"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'admin_logged_in' not in session:
                return redirect(url_for('admin_login'))
            return f(*args, **kwargs)
        return decorated_function

    def init_db():
        with sqlite3.connect("database.db") as conn:
            # Tabela de respostas do formulário
            conn.execute("""
                CREATE TABLE IF NOT EXISTS respostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    sobrenome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    telefone TEXT,
                    whatsapp TEXT,
                    cidade TEXT,
                    uf TEXT,
                    movimento TEXT,
                    sindicato TEXT,
                    area_tecnologia TEXT,
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
            
            # Verifica se já existe um usuário admin, se não cria um padrão
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM admin_users WHERE username = 'admin'")
            admin_exists = cursor.fetchone()[0]
            
            if admin_exists == 0:
                # Cria usuário admin padrão: admin / admin123
                # IMPORTANTE: Altere essa senha em produção!
                default_password = "admin123"
                password_hash = hash_password(default_password)
                cursor.execute(
                    "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
                    ("admin", password_hash)
                )
                conn.commit()
                logger.info("Usuário admin padrão criado. Username: admin, Password: admin123")
                logger.warning("IMPORTANTE: Altere a senha padrão em produção!")
            else:
                logger.info("Usuário admin já existe no banco de dados")

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
    def enviar():
        try:
            # Validação de CSRF
            if not csrf.validate():
                logger.warning(f"CSRF validation failed from IP: {request.remote_addr}")
                return jsonify({"error": "Erro de validação CSRF"}), 403

            # Sanitização e validação dos inputs
            nome = sanitize_input(request.form.get('nome', ''))
            sobrenome = sanitize_input(request.form.get('sobrenome', ''))
            email = sanitize_input(request.form.get('email', ''))
            telefone = sanitize_input(request.form.get('telefone', ''))
            whatsapp = sanitize_input(request.form.get('whatsapp', ''))
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

            if not nome or not sobrenome or not email or not whatsapp:
                logger.warning(f"Campos obrigatórios ausentes: nome, sobrenome, email, whatsapp. IP: {request.remote_addr}")
                return jsonify({"error": "Preencha todos os campos obrigatórios: nome, sobrenome, email e WhatsApp."}), 400

            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                logger.warning(f"Email inválido: {email} IP: {request.remote_addr}")
                return jsonify({"error": "Email inválido"}), 400

            if not whatsapp.isdigit() or len(whatsapp) != 11:
                logger.warning(f"WhatsApp inválido: {whatsapp} IP: {request.remote_addr}")
                return jsonify({"error": "WhatsApp deve conter 11 dígitos (DDD+telefone)"}), 400

            imagem = request.files.get('imagem')
            imagem_path = ''
            if imagem and imagem.filename != '':
                if not allowed_file(imagem.filename):
                    return jsonify({"error": "Tipo de arquivo não permitido"}), 400
                
                filename = secure_filename(imagem.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagem.save(imagem_path)

            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO respostas (
                        nome, sobrenome, email, telefone, whatsapp, cidade, uf,
                        movimento, sindicato, area_tecnologia, empresa,
                        estuda, curso, instituicao, mensagem, imagem, ip_address
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    nome, sobrenome, email, telefone, whatsapp, cidade, uf,
                    movimento, sindicato, area_tecnologia, empresa,
                    estuda, curso, instituicao, mensagem, imagem_path, request.remote_addr
                ))
                conn.commit()

            return jsonify({"message": "Resposta enviada com sucesso!"}), 200

        except Exception as e:
            logger.error(f"Erro ao processar requisição: {str(e)}")
            return jsonify({"error": "Erro ao processar a requisição"}), 500

    # ROTAS DE ADMINISTRAÇÃO
    @app.route('/admin/login', methods=['GET', 'POST'])
    @limiter.limit("10 per minute")
    def admin_login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Username e senha são obrigatórios', 'error')
                return render_template('admin/login.html')
            
            try:
                with sqlite3.connect("database.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT id, password_hash, is_active FROM admin_users WHERE username = ?",
                        (username,)
                    )
                    user = cursor.fetchone()
                    
                    if user and user[2] and check_password(password, user[1]):  # user[2] = is_active
                        session['admin_logged_in'] = True
                        session['admin_user_id'] = user[0]
                        session['admin_username'] = username
                        
                        # Atualiza último login
                        cursor.execute(
                            "UPDATE admin_users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                            (user[0],)
                        )
                        conn.commit()
                        
                        logger.info(f"Admin login successful: {username} from IP: {request.remote_addr}")
                        flash('Login realizado com sucesso!', 'success')
                        return redirect(url_for('admin_dashboard'))
                    else:
                        logger.warning(f"Failed admin login attempt: {username} from IP: {request.remote_addr}")
                        flash('Username ou senha inválidos', 'error')
                        
            except Exception as e:
                logger.error(f"Erro no login admin: {str(e)}")
                flash('Erro interno do servidor', 'error')
        
        return render_template('admin/login.html')

    @app.route('/admin/logout')
    def admin_logout():
        if 'admin_username' in session:
            logger.info(f"Admin logout: {session['admin_username']}")
        session.clear()
        flash('Logout realizado com sucesso!', 'info')
        return redirect(url_for('admin_login'))

    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = 20  # 20 registros por página
            offset = (page - 1) * per_page
            
            search = request.args.get('search', '').strip()
            
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                
                # Query base
                base_query = """
                    SELECT id, nome, sobrenome, email, whatsapp, cidade, uf, 
                           movimento, sindicato, area_tecnologia, empresa, 
                           estuda, curso, instituicao, mensagem, ip_address, created_at
                    FROM respostas
                """
                
                # Adiciona filtro de pesquisa se necessário
                if search:
                    search_query = base_query + """
                        WHERE nome LIKE ? OR sobrenome LIKE ? OR email LIKE ? 
                           OR cidade LIKE ? OR empresa LIKE ?
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    """
                    search_param = f"%{search}%"
                    cursor.execute(search_query, (search_param, search_param, search_param, 
                                                search_param, search_param, per_page, offset))
                    
                    # Conta total para paginação
                    cursor.execute("""
                        SELECT COUNT(*) FROM respostas 
                        WHERE nome LIKE ? OR sobrenome LIKE ? OR email LIKE ? 
                           OR cidade LIKE ? OR empresa LIKE ?
                    """, (search_param, search_param, search_param, search_param, search_param))
                else:
                    cursor.execute(base_query + " ORDER BY created_at DESC LIMIT ? OFFSET ?", 
                                 (per_page, offset))
                    
                    # Conta total para paginação
                    cursor.execute("SELECT COUNT(*) FROM respostas")
                
                respostas = cursor.fetchall()
                total_records = cursor.fetchone()[0]
                
                # Calcula informações de paginação
                total_pages = (total_records + per_page - 1) // per_page
                has_prev = page > 1
                has_next = page < total_pages
                
                return render_template('admin/dashboard.html', 
                                     respostas=respostas,
                                     current_page=page,
                                     total_pages=total_pages,
                                     has_prev=has_prev,
                                     has_next=has_next,
                                     total_records=total_records,
                                     search=search)
                
        except Exception as e:
            logger.error(f"Erro no dashboard admin: {str(e)}")
            flash('Erro ao carregar dashboard', 'error')
            return render_template('admin/dashboard.html', respostas=[], 
                                 current_page=1, total_pages=1, has_prev=False, 
                                 has_next=False, total_records=0, search='')

    @app.route('/admin/resposta/<int:resposta_id>')
    @admin_required
    def admin_resposta_detail(resposta_id):
        try:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM respostas WHERE id = ?
                """, (resposta_id,))
                resposta = cursor.fetchone()
                
                if not resposta:
                    flash('Resposta não encontrada', 'error')
                    return redirect(url_for('admin_dashboard'))
                
                return render_template('admin/resposta_detail.html', resposta=resposta)
                
        except Exception as e:
            logger.error(f"Erro ao buscar resposta {resposta_id}: {str(e)}")
            flash('Erro ao carregar resposta', 'error')
            return redirect(url_for('admin_dashboard'))

    # Inicializa o banco de dados quando a aplicação é criada
    init_db()
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
