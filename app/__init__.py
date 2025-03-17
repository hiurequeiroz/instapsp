from flask import Flask, redirect, url_for
from .extensions import db, login_manager, mail
import os
from .cli import init_cli
from flask_migrate import Migrate
from markdown import markdown
from pathlib import Path
from dotenv import load_dotenv
from app.config import Config
from .utils.filters import local_time
from flask_login import current_user

# Importe todos os modelos aqui para o Alembic detectá-los
from .models.user import User
from .models.post import Post
from .models.comment import Comment
from .models.like import Like
from .models.tag import Tag
from .models.visibility import Visibility
from .models.timeline_preference import TimelinePreference

load_dotenv()

def create_app(config_class=Config):
    """
    Função factory para criar a aplicação Flask
    Permite múltiplas instâncias da aplicação e facilita os testes
    """
    app = Flask(__name__,
        static_folder='static',
        static_url_path='/static',
        template_folder='templates'
    )
    
    app.config.from_object(config_class)
    Config.init_app(app)
    
    # Garantir que as pastas necessárias existam
    Path(app.instance_path).mkdir(exist_ok=True)
    Path(app.config.get('UPLOAD_FOLDER', 'uploads')).mkdir(exist_ok=True)

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

    app.jinja_env.filters['local_time'] = local_time

    # Define a página inicial como login para usuários não autenticados
    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return redirect(url_for('posts.feed'))  # Renomear a rota atual de posts para 'feed'

    return app 