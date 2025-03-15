import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from .models.user import User
from .models.post import Post
from .models.comment import Comment
from .models.like import Like
from .models.tag import Tag
from .models.visibility import Visibility
from .models.timeline_preference import TimelinePreference
from .extensions import db
from sqlalchemy import text
import os
import sqlite3
from datetime import datetime
import shutil

def init_db():
    """Inicializa o banco de dados com todas as tabelas"""
    print("Iniciando criação do banco de dados...")
    try:
        # Garante que o diretório instance existe
        instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        
        print(f"Usando banco de dados em: {db.engine.url}")
        
        # Cria cada tabela separadamente
        statements = [
            """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) NOT NULL UNIQUE,
                password_hash VARCHAR(120) NOT NULL,
                reset_code VARCHAR(8) UNIQUE,
                reset_code_expiry DATETIME,
                is_admin BOOLEAN DEFAULT FALSE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS post (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path VARCHAR(255) NOT NULL,
                caption TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS comment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(post_id) REFERENCES post(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS like (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(post_id) REFERENCES post(id),
                UNIQUE(user_id, post_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tag (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(post_id) REFERENCES post(id),
                UNIQUE(user_id, post_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS visibility (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                is_visible BOOLEAN DEFAULT TRUE,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(post_id) REFERENCES post(id),
                UNIQUE(user_id, post_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS timeline_preference (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                sort_by VARCHAR(20) DEFAULT 'recent',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES user(id)
            )
            """
        ]

        print("Criando tabelas...")
        for stmt in statements:
            print(f"Executando: {stmt.strip().split('(')[0]}")
            db.session.execute(text(stmt))
            db.session.commit()
        
        # Verifica se as tabelas foram criadas
        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = result.fetchall()
        
        print("\nTabelas criadas:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Cria um usuário admin se não existir
        print("\nVerificando usuário admin...")
        result = db.session.execute(text("SELECT * FROM user WHERE username = 'admin'"))
        admin = result.fetchone()
        
        if not admin:
            db.session.execute(text("""
                INSERT INTO user (username, password_hash, is_admin)
                VALUES ('admin', :password_hash, TRUE)
            """), {'password_hash': generate_password_hash('admin')})
            db.session.commit()
            print("✅ Usuário admin criado com sucesso!")
        else:
            print("✅ Usuário admin já existe!")
        
        print("\n✅ Banco de dados inicializado com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro ao inicializar banco de dados: {str(e)}")
        if db.session:
            db.session.rollback()

def create_backup():
    """Cria backup dos bancos de dados"""
    try:
        # Define o timestamp para o nome do backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups/database'
        
        # Cria diretório de backups se não existir
        os.makedirs(backup_dir, exist_ok=True)
        
        print(f"\n💾 Iniciando backup dos bancos de dados...")
        
        # Lista de bancos para backup
        dbs = ['app.db', 'insta.db']
        
        for db_name in dbs:
            db_path = os.path.join('instance', db_name)
            if os.path.exists(db_path):
                print(f"\n🗄️  Fazendo backup de {db_name}...")
                
                # Nome do arquivo de backup
                backup_file = os.path.join(backup_dir, f'{db_name}.{timestamp}.backup')
                
                # Faz uma cópia direta do arquivo do banco
                shutil.copy2(db_path, backup_file)
                
                size = os.path.getsize(backup_file) / (1024*1024)  # Converte para MB
                print(f"✅ {db_name} salvo com sucesso")
        
        print(f"\n✅ Backup concluído com sucesso!")
        
        # Lista os últimos 5 backups de cada banco
        print("\n📋 Últimos backups:")
        for db_name in dbs:
            backups = sorted([f for f in os.listdir(backup_dir) if f.startswith(db_name)], reverse=True)
            if backups:
                print(f"\n{db_name}:")
                for backup in backups[:5]:
                    size = os.path.getsize(os.path.join(backup_dir, backup)) / (1024*1024)  # Converte para MB
                    print(f"- {backup} ({size:.1f}MB)")
        
    except Exception as e:
        print(f"\n❌ Erro durante o backup: {str(e)}")

@click.command('backup')
@with_appcontext
def backup():
    """Cria backup dos bancos de dados"""
    try:
        # Define o timestamp para o nome do backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups/database'
        
        # Cria o diretório de backup se não existir
        os.makedirs(backup_dir, exist_ok=True)
        
        # Lista de bancos para fazer backup
        dbs = ['app.db']
        
        for db_name in dbs:
            db_path = os.path.join('instance', db_name)
            if not os.path.exists(db_path):
                print(f"\n⚠️ Banco {db_name} não encontrado, pulando...")
                continue
                
            backup_path = os.path.join(backup_dir, f'{db_name}.{timestamp}.backup')
            
            # Faz uma cópia direta do arquivo do banco
            shutil.copy2(db_path, backup_path)
            
            size = os.path.getsize(backup_path) / (1024*1024)  # Converte para MB
            print(f"\n✅ Backup de {db_name} criado: {backup_path} ({size:.1f}MB)")
        
        # Lista os últimos 5 backups
        print("\n📋 Últimos backups:")
        for db_name in dbs:
            backups = sorted([f for f in os.listdir(backup_dir) if f.startswith(db_name)], reverse=True)
            if backups:
                print(f"\n{db_name}:")
                for backup in backups[:5]:
                    size = os.path.getsize(os.path.join(backup_dir, backup)) / (1024*1024)
                    print(f"- {backup} ({size:.1f}MB)")
        
    except Exception as e:
        print(f"\n❌ Erro durante o backup: {str(e)}")

def init_cli(app):
    """Inicializa comandos CLI"""
    app.cli.add_command(reset_password_command, "reset-user-password")
    app.cli.add_command(make_admin)
    app.cli.add_command(create_timeline_pref)
    app.cli.add_command(init_database)
    app.cli.add_command(sync_db)
    app.cli.add_command(migrate_old_db)
    app.cli.add_command(backup)
    app.cli.add_command(restore)
    app.cli.add_command(list_users)
    app.cli.add_command(create_admin)

@click.command('reset-user-password')
@click.argument('username')
@click.argument('new_password')
@with_appcontext
def reset_password_command(username, new_password):
    """Redefine a senha de um usuário pelo terminal.
    Uso: flask reset-user-password NOME_USUARIO NOVA_SENHA"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        click.echo('Erro: Usuário não encontrado.')
        return
    
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    click.echo(f'Senha alterada com sucesso para o usuário {username}')

@click.command('make-admin')
@click.argument('username')
@with_appcontext
def make_admin(username):
    """Torna um usuário administrador"""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo('Usuário não encontrado.')
        return
    
    user.is_admin = True
    db.session.commit()
    click.echo(f'Usuário {username} agora é administrador.')

@click.command('create-timeline-pref')
@with_appcontext
def create_timeline_pref():
    """Cria a tabela timeline_preference se ela não existir"""
    print("Iniciando verificação da tabela timeline_preference...")
    try:
        # Verifica se a tabela existe
        print("Verificando se a tabela existe...")
        result = db.session.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='timeline_preference';
        """))
        
        if not result.fetchone():
            print("Tabela não encontrada. Criando...")
            # Cria a tabela
            db.session.execute(text("""
                CREATE TABLE timeline_preference (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    sort_by VARCHAR(20) DEFAULT 'recent',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES user(id)
                );
            """))
            db.session.commit()
            print("✅ Tabela timeline_preference criada com sucesso!")
        else:
            print("✅ Tabela timeline_preference já existe!")
    except Exception as e:
        print(f"❌ Erro ao verificar/criar tabela: {str(e)}")
        db.session.rollback()

@click.command('init-db')
@with_appcontext
def init_database():
    """Inicializa o banco de dados"""
    init_db()

@click.command('sync-db')
@with_appcontext
def sync_db():
    """Sincroniza o banco de dados"""
    db.drop_all()
    db.create_all()
    print('Banco de dados sincronizado!')

@click.command('migrate-old-db')
@with_appcontext
def migrate_old_db():
    """Migra dados do banco antigo para o novo"""
    try:
        old_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance/insta.db')
        if not os.path.exists(old_db_path):
            print("❌ Banco de dados antigo não encontrado!")
            return

        print(f"Migrando dados de: {old_db_path}")
        
        # Conecta ao banco antigo
        from sqlite3 import connect as sqlite_connect
        old_conn = sqlite_connect(old_db_path)
        old_cur = old_conn.cursor()
        
        # Primeiro, verifica as tabelas disponíveis
        old_cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = old_cur.fetchall()
        print("\nTabelas encontradas no banco antigo:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Continua apenas se encontrou tabelas
        if not tables:
            print("❌ Nenhuma tabela encontrada no banco antigo!")
            return
            
        # Migra usuários
        print("\nMigrando usuários...")
        old_cur.execute("SELECT * FROM user")
        users = old_cur.fetchall()
        for user in users:
            db.session.execute(text("""
                INSERT OR IGNORE INTO user (id, username, password_hash, reset_code, reset_code_expiry, is_admin)
                VALUES (:id, :username, :password_hash, :reset_code, :reset_code_expiry, :is_admin)
            """), {
                'id': user[0],
                'username': user[1],
                'password_hash': user[2],
                'reset_code': user[3],
                'reset_code_expiry': user[4],
                'is_admin': user[5]
            })
        print(f"✅ {len(users)} usuários migrados")
        
        # Migra posts
        print("\nMigrando posts...")
        old_cur.execute("SELECT * FROM post")
        posts = old_cur.fetchall()
        for post in posts:
            db.session.execute(text("""
                INSERT OR IGNORE INTO post (id, image_path, caption, created_at, user_id)
                VALUES (:id, :image_path, :caption, :created_at, :user_id)
            """), {
                'id': post[0],
                'image_path': post[1],
                'caption': post[2],
                'created_at': post[3],
                'user_id': post[4]
            })
        print(f"✅ {len(posts)} posts migrados")
        
        # Migra comentários
        print("\nMigrando comentários...")
        old_cur.execute("SELECT * FROM comment")
        comments = old_cur.fetchall()
        for comment in comments:
            db.session.execute(text("""
                INSERT OR IGNORE INTO comment (id, text, created_at, user_id, post_id)
                VALUES (:id, :text, :created_at, :user_id, :post_id)
            """), {
                'id': comment[0],
                'text': comment[1],
                'created_at': comment[2],
                'user_id': comment[3],
                'post_id': comment[4]
            })
        print(f"✅ {len(comments)} comentários migrados")
        
        # Migra curtidas
        print("\nMigrando curtidas...")
        old_cur.execute("SELECT * FROM like")
        likes = old_cur.fetchall()
        for like in likes:
            db.session.execute(text("""
                INSERT OR IGNORE INTO like (id, user_id, post_id, created_at)
                VALUES (:id, :user_id, :post_id, :created_at)
            """), {
                'id': like[0],
                'user_id': like[1],
                'post_id': like[2],
                'created_at': like[3]
            })
        print(f"✅ {len(likes)} curtidas migradas")
        
        # Migra tags
        print("\nMigrando tags...")
        old_cur.execute("SELECT * FROM tag")
        tags = old_cur.fetchall()
        for tag in tags:
            db.session.execute(text("""
                INSERT OR IGNORE INTO tag (id, user_id, post_id, created_at)
                VALUES (:id, :user_id, :post_id, :created_at)
            """), {
                'id': tag[0],
                'user_id': tag[1],
                'post_id': tag[2],
                'created_at': tag[3]
            })
        print(f"✅ {len(tags)} tags migradas")
        
        # Migra visibilidade
        print("\nMigrando visibilidade...")
        old_cur.execute("SELECT * FROM visibility")
        visibilities = old_cur.fetchall()
        for vis in visibilities:
            db.session.execute(text("""
                INSERT OR IGNORE INTO visibility (id, user_id, post_id, is_visible)
                VALUES (:id, :user_id, :post_id, :is_visible)
            """), {
                'id': vis[0],
                'user_id': vis[1],
                'post_id': vis[2],
                'is_visible': vis[3]
            })
        print(f"✅ {len(visibilities)} configurações de visibilidade migradas")
        
        db.session.commit()
        old_conn.close()
        
        print("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {str(e)}")
        if db.session:
            db.session.rollback()

@click.command('restore')
@click.argument('backup_file', required=False)
@with_appcontext
def restore(backup_file=None):
    """Restaura um backup do banco de dados"""
    try:
        backup_dir = 'backups/database'
        
        # Se nenhum arquivo específico foi fornecido, lista os backups disponíveis
        if not backup_file:
            if not os.path.exists(backup_dir):
                print("❌ Nenhum backup encontrado!")
                return
                
            backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.backup')], reverse=True)
            if not backups:
                print("❌ Nenhum backup encontrado!")
                return
                
            print("\n📋 Backups disponíveis:")
            for i, backup in enumerate(backups, 1):
                size = os.path.getsize(os.path.join(backup_dir, backup)) / (1024*1024)  # MB
                print(f"{i}. {backup} ({size:.1f}MB)")
            
            try:
                choice = input("\nEscolha o número do backup para restaurar (ou 'q' para sair): ")
                if choice.lower() == 'q':
                    return
                    
                backup_file = backups[int(choice) - 1]
            except (ValueError, IndexError):
                print("❌ Escolha inválida!")
                return
        
        backup_path = os.path.join(backup_dir, backup_file)
        if not os.path.exists(backup_path):
            print(f"❌ Arquivo de backup não encontrado: {backup_file}")
            return
            
        print(f"\n🔄 Restaurando backup: {backup_file}")
        
        # Determina se é app.db ou insta.db baseado no nome do arquivo
        if backup_file.startswith('app.db'):
            db_name = 'app.db'
        elif backup_file.startswith('insta.db'):
            db_name = 'insta.db'
        else:
            print("❌ Nome de arquivo de backup inválido!")
            return
            
        # Cria backup do banco atual antes de restaurar
        current_db_path = os.path.join('instance', db_name)
        if os.path.exists(current_db_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pre_restore_backup = os.path.join(backup_dir, f'{db_name}.pre_restore.{timestamp}.backup')
            print(f"\n💾 Criando backup de segurança: {os.path.basename(pre_restore_backup)}")
            shutil.copy2(current_db_path, pre_restore_backup)
        
        print("\n🔄 Iniciando restauração...")
        
        # Copia o arquivo de backup diretamente para o local do banco de dados
        shutil.copy2(backup_path, current_db_path)
        
        print("\n✅ Backup restaurado com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a restauração: {str(e)}")

@click.command('list-users')
@with_appcontext
def list_users():
    """Lista todos os usuários no banco de dados"""
    try:
        users = User.query.all()
        if not users:
            print("\n❌ Nenhum usuário encontrado no banco de dados!")
            return
            
        print("\n📋 Usuários cadastrados:")
        for user in users:
            print(f"- {user.username} {'(Admin)' if user.is_admin else ''}")
            
    except Exception as e:
        print(f"\n❌ Erro ao listar usuários: {str(e)}")

@click.command('create-admin')
@click.argument('username')
@click.argument('password')
@with_appcontext
def create_admin(username, password):
    """Cria um novo usuário administrador"""
    try:
        from werkzeug.security import generate_password_hash
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        print(f"\n✅ Usuário administrador '{username}' criado com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Erro ao criar usuário: {str(e)}") 