import os
import shutil
from datetime import datetime
import sqlite3

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
                
                # Cria backup usando SQLite
                conn = sqlite3.connect(db_path)
                with open(backup_file, 'w') as f:
                    for line in conn.iterdump():
                        f.write(line + '\n')
                conn.close()
                
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