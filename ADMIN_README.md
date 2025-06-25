# Sistema de Administração - ComunaTec

## 🔐 Funcionalidades de Segurança Implementadas

O sistema de administração foi desenvolvido seguindo as melhores práticas de segurança:

### Autenticação e Autorização
- ✅ Hash de senhas com bcrypt (salt automático)
- ✅ Sessões Flask seguras
- ✅ Rate limiting nos endpoints (10 tentativas por minuto no login)
- ✅ Decorator `@admin_required` para proteger rotas
- ✅ Validação CSRF em todos os formulários
- ✅ Headers de segurança (XSS Protection, Content Security Policy, etc.)

### Controle de Acesso
- ✅ Usuário admin padrão criado automaticamente
- ✅ Sistema de logout seguro (limpa toda a sessão)
- ✅ Logs de auditoria (login/logout/tentativas falhadas)
- ✅ Verificação de usuário ativo

## 🚀 Como Acessar o Sistema

### 1. Iniciar a Aplicação
```bash
python app.py
```

### 2. Acessar a Área Administrativa
- URL: `http://localhost:5001/admin/login`
- **Usuário padrão:** `admin`
- **Senha padrão:** `admin123`

⚠️ **IMPORTANTE:** Altere a senha padrão em produção!

### 3. Navegação no Sistema
- **Dashboard:** Visualizar todas as respostas do formulário
- **Busca:** Pesquisar por nome, email, cidade ou empresa
- **Detalhes:** Ver informações completas de cada resposta
- **Paginação:** Navegar entre páginas (20 registros por página)

## 📊 Funcionalidades do Dashboard

### Visualização de Dados
- **Tabela responsiva** com informações essenciais
- **Links diretos** para WhatsApp e email
- **Badges** para destacar informações importantes
- **Paginação inteligente** com navegação rápida

### Sistema de Busca
- Busca em **tempo real** por:
  - Nome e sobrenome
  - Email
  - Cidade
  - Empresa
- **Filtros persistentes** na paginação

### Detalhes das Respostas
- **Cards organizados** por categoria:
  - Informações Pessoais
  - Localização (com IP de origem)
  - Movimentos e Sindicatos
  - Informações Profissionais
  - Dados Educacionais
  - Mensagens
  - Imagens anexadas

### Ações Disponíveis
- **Envio direto de email** (mailto)
- **Contato via WhatsApp** (link direto)
- **Impressão** de relatórios
- **Visualização de imagens** anexadas

## 🛡️ Segurança da Aplicação

### Proteções Implementadas
1. **Sanitização de inputs** - Remove caracteres perigosos
2. **Validação rigorosa** - Email, WhatsApp, campos obrigatórios
3. **Rate limiting** - Previne ataques de força bruta
4. **CSRF tokens** - Proteção contra ataques cross-site
5. **Headers de segurança** - XSS, clickjacking, etc.
6. **Logs de auditoria** - Rastreamento de ações

### Estrutura do Banco de Dados
```sql
-- Tabela de usuários admin
admin_users:
- id (PRIMARY KEY)
- username (UNIQUE)
- password_hash (bcrypt)
- created_at
- last_login
- is_active

-- Tabela de respostas (existente)
respostas:
- id, nome, sobrenome, email, telefone, whatsapp
- cidade, uf, movimento, sindicato
- area_tecnologia, empresa, estuda, curso, instituicao
- mensagem, imagem, ip_address, created_at
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```bash
# Chave secreta (OBRIGATÓRIO em produção)
export SECRET_KEY="sua-chave-secreta-super-forte"

# Redis para Rate Limiter (recomendado para produção)
export REDIS_URL="redis://localhost:6379/0"

# Configurações de banco (opcional)
export DATABASE_URL="sqlite:///database.db"

# Ambiente (opcional)
export FLASK_ENV="production"
```

### Criação de Novos Admins
Para criar novos usuários admin, acesse o banco diretamente:

```python
import bcrypt
import sqlite3

# Hash da nova senha
password = "nova_senha_forte"
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Inserir no banco
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute(
    "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
    ("novo_admin", password_hash)
)
conn.commit()
conn.close()
```

## 📝 Logs e Monitoramento

### Arquivo de Log: `app.log`
- Logs de **login/logout** de admins
- **Tentativas falhadas** de acesso
- **Erros** da aplicação
- **IPs** de origem das ações

### Exemplo de Log:
```
2025-06-25 13:05:12,707 - INFO - Admin login successful: admin from IP: 127.0.0.1
2025-06-25 13:05:12,707 - WARNING - Failed admin login attempt: hacker from IP: 192.168.1.100
```

## 🎨 Interface e UX

### Design Responsivo
- **Bootstrap 5** para layout moderno
- **Font Awesome** para ícones
- **Cores da marca** ComunaTec (vermelho #cc0000)
- **Mobile-first** design

### Experiência do Usuário
- **Feedback visual** para todas as ações
- **Loading states** e mensagens de erro claras
- **Navegação intuitiva** com breadcrumbs
- **Atalhos de teclado** (Enter para login)

## 🚀 Deploy em Produção

### Configurações Obrigatórias
1. **Alterar senha padrão** do admin
2. **Definir SECRET_KEY** forte
3. **Configurar HTTPS** (SSL/TLS)
4. **Configurar backup** do banco de dados
5. **Limitar IPs** de acesso se necessário

### Exemplo com Docker
```dockerfile
# Dockerfile já está configurado
docker build -t comunatec-admin .
docker run -p 5001:5001 -e SECRET_KEY="sua-chave-super-secreta" comunatec-admin
```

## ❓ Solução de Problemas

### Flask-Limiter Warning (Rate Limiter)
**Warning:** `Using the in-memory storage for tracking rate limits`

**Soluções:**
1. **Desenvolvimento:** O warning foi suprimido, mas funciona normalmente
2. **Produção:** Configure Redis para performance otimizada:
   ```bash
   # Instalar Redis
   sudo apt-get install redis-server
   # ou
   docker run -p 6379:6379 redis:alpine
   
   # Configurar variável de ambiente
   export REDIS_URL="redis://localhost:6379/0"
   ```

### Problemas Comuns
1. **Erro de CSRF**: Verifique se os tokens estão sendo enviados
2. **Rate limiting**: Aguarde alguns minutos entre tentativas
3. **Sessão expirada**: Faça login novamente
4. **Permissões**: Verifique se o usuário está ativo

### Comandos Úteis
```bash
# Verificar estrutura do banco
sqlite3 database.db ".schema"

# Ver usuários admin
sqlite3 database.db "SELECT * FROM admin_users;"

# Resetar tentativas de rate limiting (reiniciar app)
```

---

## 🎯 Resumo das URLs

- **Site principal:** `http://localhost:5001/`
- **Login admin:** `http://localhost:5001/admin/login`
- **Dashboard:** `http://localhost:5001/admin/dashboard`
- **Logout:** `http://localhost:5001/admin/logout`

---

**Desenvolvido com ❤️ seguindo as melhores práticas de segurança para o ComunaTec** 