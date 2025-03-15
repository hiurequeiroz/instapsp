from flask import Flask
from .config import Config
from .extensions import db, login_manager, mail
import os
from .cli import init_cli
from flask_migrate import Migrate
from markdown import markdown
from pathlib import Path
from dotenv import load_dotenv

# Importe todos os modelos aqui para o Alembic detectá-los
from .models.user import User
from .models.post import Post
from .models.comment import Comment
from .models.like import Like
from .models.tag import Tag
from .models.visibility import Visibility
from .models.timeline_preference import TimelinePreference

load_dotenv()

def create_app(test_config=None):
    """
    Função factory para criar a aplicação Flask
    Permite múltiplas instâncias da aplicação e facilita os testes
    """
    app = Flask(__name__)
    
    # Configurações básicas
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, os.getenv('DATABASE_NAME', 'database.db')),
        UPLOAD_FOLDER=os.getenv('UPLOAD_FOLDER', 'uploads'),
        MAX_CONTENT_LENGTH=int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    )
    
    # Garantir que as pastas necessárias existam
    Path(app.instance_path).mkdir(exist_ok=True)
    Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

    # Inicializa as extensões com a app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)

    migrate = Migrate(app, db)

    # Registra os blueprints
    from .routes import auth, posts, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(admin.bp)

    # Inicializa CLI
    init_cli(app)

    # Adiciona o filtro markdown
    @app.template_filter('markdown')
    def markdown_filter(text):
        return markdown(text) if text else ''

    return app 