import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações padrão da aplicação"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///vendiAI.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Limites de planos
    PLAN_LIMITS = {
        'free': 5,
        'starter': 100,
        'pro': 500,
        'enterprise': float('inf')
    }
    
    # Preços em BRL
    PLAN_PRICES = {
        'free': 0,
        'starter': 9.90,
        'pro': 29.90,
        'enterprise': 99.90
    }

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configurações para testes"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Selecionar config baseada no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
