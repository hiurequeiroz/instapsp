import os

class Config:
    """Configurações da aplicação"""
    
    # Definir basedir como atributo de classe
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Chave secreta para sessões e tokens
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'você-nunca-vai-adivinhar'
    
    # Configuração do SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '../instance/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuração de upload
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_PDF_EXTENSIONS = {'pdf'}
    
    # Configurações de email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'seu-email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'sua-senha-de-app'
    
    SEND_FILE_MAX_AGE_DEFAULT = 0
    TEMPLATES_AUTO_RELOAD = True

    @staticmethod
    def init_app(app):
        # Usar o basedir da classe
        os.makedirs(os.path.join(Config.basedir, '../instance'), exist_ok=True)
        os.makedirs(os.path.join(Config.basedir, '../uploads'), exist_ok=True) 