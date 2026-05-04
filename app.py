from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import openai
import os
from dotenv import load_dotenv
from datetime import datetime
from functools import wraps

load_dotenv()

# Inicializar Flask e SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///vendiAI.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configurar OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# ============ MODELOS DO BANCO DE DADOS ============

class User(db.Model):
    """Modelo de usuário"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    plan = db.Column(db.String(20), default='free')  # free, starter, pro, enterprise
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    generations = db.relationship('Generation', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Generation(db.Model):
    """Modelo para cada geração de conteúdo"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'mensagem_venda', 'proposta', 'post', 'email'
    input_text = db.Column(db.Text, nullable=False)
    output_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============ DECORADORES ============

def login_required(f):
    """Verifica se o usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============ ROTAS - AUTENTICAÇÃO ============

@app.route('/')
def index():
    """Página inicial"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registrar novo usuário"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Validar
        if not username or not email or not password:
            return jsonify({'error': 'Preencha todos os campos'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Usuário já existe'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email já registrado'}), 400

        # Criar usuário
        user = User(username=username, email=email, plan='free')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'Registrado com sucesso!'}), 201

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Fazer login"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Usuário ou senha inválidos'}), 401

        session['user_id'] = user.id
        session['username'] = user.username
        session['plan'] = user.plan

        return jsonify({'message': 'Login realizado!'}), 200

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Fazer logout"""
    session.clear()
    return redirect(url_for('index'))


# ============ ROTAS - DASHBOARD ============

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard do usuário"""
    user = User.query.get(session['user_id'])
    generations = Generation.query.filter_by(user_id=user.id).order_by(Generation.created_at.desc()).all()
    
    # Contar gerações do mês atual
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)
    month_generations = Generation.query.filter(
        Generation.user_id == user.id,
        Generation.created_at >= month_start
    ).count()
    
    # Limites de plano
    plan_limits = {
        'free': 5,
        'starter': 100,
        'pro': 500,
        'enterprise': float('inf')
    }
    
    limit = plan_limits.get(user.plan, 5)
    remaining = max(0, limit - month_generations)

    return render_template('dashboard.html', 
                         user=user, 
                         generations=generations,
                         month_generations=month_generations,
                         remaining=remaining,
                         limit=limit)


# ============ ROTAS - API (Geração de Conteúdo) ============

@app.route('/api/generate', methods=['POST'])
@login_required
def generate_content():
    """Gerar conteúdo com IA"""
    data = request.get_json()
    content_type = data.get('content_type')
    user_input = data.get('user_input')

    if not content_type or not user_input:
        return jsonify({'error': 'Dados incompletos'}), 400

    user = User.query.get(session['user_id'])

    # Verificar limite de plano
    plan_limits = {
        'free': 5,
        'starter': 100,
        'pro': 500,
        'enterprise': float('inf')
    }

    from datetime import datetime
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)
    month_generations = Generation.query.filter(
        Generation.user_id == user.id,
        Generation.created_at >= month_start
    ).count()

    if month_generations >= plan_limits.get(user.plan, 5):
        return jsonify({'error': f'Limite de {plan_limits.get(user.plan, 5)} gerações atingido este mês. Atualize seu plano!'}), 403

    # Prompts customizados para cada tipo
    prompts = {
        'mensagem_venda': f"""Crie uma mensagem de venda profissional e persuasiva baseada nisso:
{user_input}

A mensagem deve:
- Ser curta (máximo 3 parágrafos)
- Ter um CTA (Call To Action) claro
- Ser convincente e focar em benefícios
- Ser apropriada para WhatsApp/Instagram

Retorne apenas a mensagem, sem explicações.""",

        'proposta': f"""Crie uma proposta/orçamento profissional baseado nisso:
{user_input}

A proposta deve:
- Ter estrutura clara (Descrição, Valor, Prazos)
- Ser profissional
- Incluir termos de condição de pagamento

Retorne apenas a proposta formatada.""",

        'post_redes': f"""Crie um post profissional para redes sociais (Instagram/Facebook) baseado nisso:
{user_input}

O post deve:
- Ser atrativo e engajador
- Ter emoji apropriados
- Incluir hashtags relevantes
- Ter máximo 300 caracteres

Retorne apenas o post, sem explicações.""",

        'email': f"""Crie um email de venda profissional baseado nisso:
{user_input}

O email deve:
- Ter subject line atrativo
- Corpo bem estruturado
- CTA claro no final
- Ser profissional

Retorne o email com "SUBJECT:" no início."""
    }

    prompt = prompts.get(content_type, prompts['mensagem_venda'])

    try:
        # Chamar OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em vendas e marketing. Gere conteúdo profissional, persuasivo e de qualidade."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        generated_text = response['choices'][0]['message']['content'].strip()

        # Salvar no banco de dados
        generation = Generation(
            user_id=user.id,
            content_type=content_type,
            input_text=user_input,
            output_text=generated_text
        )
        db.session.add(generation)
        db.session.commit()

        return jsonify({
            'success': True,
            'content': generated_text,
            'id': generation.id
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao gerar conteúdo: {str(e)}'}), 500


@app.route('/api/history')
@login_required
def get_history():
    """Retornar histórico de gerações"""
    user = User.query.get(session['user_id'])
    generations = Generation.query.filter_by(user_id=user.id).order_by(Generation.created_at.desc()).limit(10).all()

    data = [
        {
            'id': g.id,
            'content_type': g.content_type,
            'input_text': g.input_text[:50] + '...',
            'created_at': g.created_at.strftime('%d/%m/%Y %H:%M')
        }
        for g in generations
    ]

    return jsonify(data), 200


@app.route('/api/delete/<int:generation_id>', methods=['DELETE'])
@login_required
def delete_generation(generation_id):
    """Deletar uma geração"""
    generation = Generation.query.get(generation_id)

    if not generation or generation.user_id != session['user_id']:
        return jsonify({'error': 'Não autorizado'}), 403

    db.session.delete(generation)
    db.session.commit()

    return jsonify({'success': True}), 200


# ============ ROTAS - PLANOS ============

@app.route('/pricing')
def pricing():
    """Página de preços"""
    plans = {
        'free': {'name': 'Free', 'price': 'Grátis', 'limit': '5 gerações/mês'},
        'starter': {'name': 'Starter', 'price': 'R$ 9,90', 'limit': '100 gerações/mês'},
        'pro': {'name': 'Pro', 'price': 'R$ 29,90', 'limit': '500 gerações/mês'},
        'enterprise': {'name': 'Enterprise', 'price': 'R$ 99,90', 'limit': 'Ilimitado'}
    }
    return render_template('pricing.html', plans=plans)


# ============ INICIALIZAÇÃO ============

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
