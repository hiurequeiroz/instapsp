import os
import shutil
from app import create_app, db
from app.config import Config
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like
from app.models.tag import Tag

def clean_database():
    """Limpa todas as entradas do banco de dados"""
    app = create_app(Config)
    with app.app_context():
        # Remove todos os registros relacionados
        Tag.query.delete()
        Like.query.delete()
        Comment.query.delete()
        Post.query.delete()
        db.session.commit()
        print("✓ Banco de dados limpo com sucesso!")

def init_folders():
    """Inicializa a estrutura de pastas do aplicativo"""
    app = create_app(Config)
    
    # Define os diretórios necessários
    static_dir = os.path.join(app.root_path, 'static')
    folders = [
        os.path.join(static_dir, 'uploads'),
        os.path.join(static_dir, 'uploads/images'),
        os.path.join(static_dir, 'uploads/pdfs'),
        os.path.join(static_dir, 'css'),
        os.path.join(static_dir, 'js'),
        os.path.join(static_dir, 'webfonts')
    ]
    
    # Cria as pastas necessárias
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Pasta criada: {folder}")
    
    print("\n✓ Estrutura de pastas inicializada com sucesso!")

def clean_uploads():
    """Limpa arquivos de upload de teste"""
    app = create_app(Config)
    uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
    
    # Limpa imagens e PDFs
    for folder in ['images', 'pdfs']:
        folder_path = os.path.join(uploads_dir, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)
            print(f"✓ Pasta limpa: {folder_path}")
    
    # Remove arquivos soltos na pasta uploads
    for file in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    print("\n✓ Arquivos de teste removidos com sucesso!")

if __name__ == "__main__":
    print("Inicializando aplicativo...\n")
    clean_database()  # Primeiro limpa o banco de dados
    init_folders()    # Depois inicializa as pastas
    clean_uploads()   # Por fim limpa os uploads
    print("\nAplicativo pronto para uso!") 