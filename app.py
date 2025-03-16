from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
import os
import time
import logging
from app import create_app
from app.config import Config

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app(Config)

# Configurar os diretórios de upload
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
PDF_FOLDER = os.path.join(UPLOAD_FOLDER, 'pdfs')
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')

# Criar diretórios se não existirem
for folder in [UPLOAD_FOLDER, PDF_FOLDER, IMAGE_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Debug dos caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logger.info("\n=== DEBUG CAMINHOS ===")
logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"Arquivo atual: {__file__}")
logger.info(f"Diretório atual: {os.getcwd()}")

# Verificar permissões
for folder in [UPLOAD_FOLDER, PDF_FOLDER, IMAGE_FOLDER]:
    logger.info(f"Pasta {folder}:")
    logger.info(f"  - Existe? {os.path.exists(folder)}")
    logger.info(f"  - Permissão de escrita? {os.access(folder, os.W_OK)}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_IMAGE_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['ALLOWED_PDF_EXTENSIONS'] = {'pdf'}

def allowed_file(filename, allowed_extensions):
    if '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def index():
    # Lista imagens e PDFs
    posts = []
    
    # Lista PDFs
    for filename in os.listdir(PDF_FOLDER):
        if filename.endswith('.pdf'):
            file_path = os.path.join(PDF_FOLDER, filename)
            title = filename.split('_', 2)[-1].replace('.pdf', '')
            posts.append({
                'type': 'pdf',
                'title': title,
                'url': url_for('static', filename=f'uploads/pdfs/{filename}'),  # Caminho correto
                'date': time.ctime(os.path.getmtime(file_path)),
                'description': 'Artigo PDF compartilhado'
            })
    
    # Lista imagens
    for filename in os.listdir(IMAGE_FOLDER):  # Usar IMAGE_FOLDER ao invés de UPLOAD_FOLDER
        if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            file_path = os.path.join(IMAGE_FOLDER, filename)
            posts.append({
                'type': 'image',
                'image_path': f'uploads/images/{filename}',  # Caminho correto para as imagens
                'date': time.ctime(os.path.getmtime(file_path)),
                'caption': ''
            })
    
    # Ordena por data, mais recente primeiro
    posts.sort(key=lambda x: os.path.getmtime(
        os.path.join(PDF_FOLDER if x['type'] == 'pdf' else UPLOAD_FOLDER,
                    x['url'].split('/')[-1] if x['type'] == 'pdf' else x['image_path'])), 
        reverse=True)
    
    return render_template('posts/index.html', posts=posts)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
            
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            return handle_pdf_upload()
        elif any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            return handle_image_upload()
        else:
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    return render_template('posts/upload.html')

def handle_pdf_upload():
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Apenas arquivos PDF são permitidos'}), 400
    
    try:
        filename = secure_filename(file.filename)
        unique_filename = f"pdf_{int(time.time())}_{filename}"
        file_path = os.path.join(PDF_FOLDER, unique_filename)
        
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'file_url': f'/static/uploads/pdfs/{unique_filename}',
            'title': request.form.get('title', ''),
            'description': request.form.get('description', '')
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao salvar arquivo: {str(e)}'}), 500

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/upload_pdf', methods=['POST'])  # Nova rota específica para PDF
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Apenas arquivos PDF são permitidos'}), 400
    
    try:
        filename = secure_filename(file.filename)
        unique_filename = f"pdf_{int(time.time())}_{filename}"
        file_path = os.path.join(PDF_FOLDER, unique_filename)
        
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'file_url': f'/static/uploads/pdfs/{unique_filename}',
            'title': request.form.get('title', ''),
            'description': request.form.get('description', '')
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao salvar arquivo: {str(e)}'}), 500

def handle_image_upload():
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not any(file.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    try:
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        file_path = os.path.join(IMAGE_FOLDER, unique_filename)  # Usa IMAGE_FOLDER
        
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'file_url': url_for('static', filename=f'uploads/images/{unique_filename}'),
            'filename': unique_filename
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao salvar arquivo: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 