from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import time
from ..extensions import db
from ..models.post import Post
from ..models.comment import Comment
from ..utils.image_handler import process_image
from ..models.like import Like
from ..models.user import User
from ..models.tag import Tag
from ..models.visibility import Visibility
from ..models.timeline_preference import TimelinePreference
from sqlalchemy import func, or_
from datetime import datetime
import pytz  # Adicione esta importação no topo do arquivo

bp = Blueprint('posts', __name__)

# Configurações de upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_upload_folders():
    """Retorna os caminhos das pastas de upload"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    pdf_folder = os.path.join(upload_folder, 'pdfs')
    image_folder = os.path.join(upload_folder, 'images')
    return upload_folder, pdf_folder, image_folder

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função auxiliar para converter UTC para horário de Brasília
def utc_to_local(utc_dt):
    local_tz = pytz.timezone('America/Sao_Paulo')
    local_dt = utc_dt.replace(tzinfo=pytz.UTC).astimezone(local_tz)
    return local_dt

@bp.route('/feed')
@login_required
def feed():
    """Feed de fotos e PDFs"""
    # Verifica preferência do usuário
    preference = TimelinePreference.query.filter_by(user_id=current_user.id).first()
    sort_by = preference.sort_by if preference else 'recent'
    admin_first = bool(preference.admin_first) if preference and preference.admin_first is not None else False

    # Busca todos os posts não ocultos
    posts = Post.query.filter(
        or_(Post.is_hidden.is_(None), Post.is_hidden == False)  # noqa
    ).order_by(Post.created_at.desc()).all()

    # Debug da ordenação admin first
    if admin_first:
        admin_posts = [p for p in posts if p.author.is_admin]
        other_posts = [p for p in posts if not p.author.is_admin]
        
        if admin_posts:
            posts = [admin_posts[0]] + other_posts + admin_posts[1:]

    # Busca PDFs
    UPLOAD_FOLDER, PDF_FOLDER, IMAGE_FOLDER = get_upload_folders()
    pdf_posts = []
    
    for filename in os.listdir(PDF_FOLDER):
        if filename.endswith('.pdf'):
            file_path = os.path.join(PDF_FOLDER, filename)
            # Extrai título e descrição do nome do arquivo
            parts = filename.split('_', 2)
            if len(parts) >= 3:
                title = parts[2].replace('.pdf', '')
                description = f"Material didático: {title}"
            else:
                title = filename.replace('.pdf', '')
                description = "Material didático compartilhado"
                
            file_timestamp = os.path.getmtime(file_path)
            local_time = datetime.fromtimestamp(file_timestamp)
            
            pdf_posts.append({
                'type': 'pdf',
                'title': title,
                'url': url_for('static', filename=f'uploads/pdfs/{filename}'),
                'created_at': local_time,
                'author': current_user,
                'description': description  # Descrição mais informativa
            })
    
    # Combina e ordena todos os posts
    all_posts = []
    all_posts.extend(posts)  # Adiciona posts de imagem
    all_posts.extend(pdf_posts)    # Adiciona PDFs
    
    # Ordena PDFs junto com as imagens conforme a preferência
    if sort_by == 'recent':
        all_posts.sort(
            key=lambda x: x['created_at'] if isinstance(x, dict) else x.created_at,
            reverse=True
        )
    
    return render_template('posts/index.html', posts=all_posts)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('posts/upload.html')
    
    UPLOAD_FOLDER, PDF_FOLDER, IMAGE_FOLDER = get_upload_folders()
    
    try:
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('posts.upload'))
            
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('posts.upload'))
            
        if not allowed_file(file.filename):
            flash('Tipo de arquivo não permitido', 'error')
            return redirect(url_for('posts.upload'))
            
        # Processa upload de imagem
        filter_name = request.form.get('filter', 'normal')
        processed_image = process_image(file, filter_name)
        
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{int(time.time())}.jpg"
        filepath = os.path.join(IMAGE_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(processed_image.getvalue())
        
        # Cria o post com o horário local
        local_tz = pytz.timezone('America/Sao_Paulo')
        local_time = datetime.now(local_tz)
        
        post = Post(
            image_path=f'uploads/images/{filename}',
            caption=request.form.get('caption', ''),
            user_id=current_user.id,
            created_at=local_time
        )
        db.session.add(post)
        db.session.commit()
        
        flash('Imagem enviada com sucesso!', 'success')
        return redirect(url_for('posts.feed'))
        
    except Exception as e:
        print(f"Erro no upload: {str(e)}")
        db.session.rollback()
        flash(f'Erro ao fazer upload: {str(e)}', 'error')
        return redirect(url_for('posts.upload'))

@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Adiciona um comentário a um post"""
    post = Post.query.get_or_404(post_id)
    text = request.form.get('text')
    
    if text:
        comment = Comment(
            text=text,
            user_id=current_user.id,
            post_id=post_id
        )
        db.session.add(comment)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'comment': {
                    'author': current_user.username,
                    'text': text,
                    'time': comment.created_at.strftime('%d/%m/%Y %H:%M')
                }
            })
    
    return redirect(url_for('posts.feed'))

@bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    """Alterna curtida em um post"""
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if like:
        db.session.delete(like)
        action = 'unliked'
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'action': action,
        'likeCount': post.like_count()
    })

@bp.route('/post/<int:post_id>/tag', methods=['POST'])
@login_required
def tag_user(post_id):
    """Marca um usuário em um post"""
    post = Post.query.get_or_404(post_id)
    username = request.json.get('username')
    
    if not username:
        return jsonify({'error': 'Nome de usuário não fornecido'}), 400
        
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
        
    # Verifica se o usuário já está marcado
    if user in post.tagged_users:
        return jsonify({'error': 'Usuário já está marcado neste post'}), 400
        
    tag = Tag(post_id=post_id, user_id=user.id)
    db.session.add(tag)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username
        }
    })

@bp.route('/users/search')
@login_required
def search_users():
    """Busca usuários para marcação"""
    query = request.args.get('q', '').strip()
    if len(query) < 1:  # Alterado para 1 para buscar desde a primeira letra
        return jsonify({'users': []})
    
    users = User.query\
        .filter(User.username.ilike(f'{query}%'))\
        .filter(User.id != current_user.id)\
        .limit(5)\
        .all()
    
    return jsonify({
        'users': [{'id': user.id, 'username': user.username} for user in users]
    })

@bp.route('/notifications')
@login_required
def notifications():
    """Página de notificações"""
    return render_template('posts/notifications.html')

@bp.route('/pdfs')
@login_required
def list_pdfs():
    """Lista todos os PDFs compartilhados"""
    pdfs = []
    pdf_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'pdfs')
    
    for filename in os.listdir(pdf_folder):
        if filename.endswith('.pdf'):
            file_path = os.path.join(pdf_folder, filename)
            title = filename.split('_', 2)[-1].replace('.pdf', '')
            pdfs.append({
                'title': title,
                'url': url_for('static', filename=f'uploads/pdfs/{filename}'),
                'date': time.ctime(os.path.getmtime(file_path)),
                'size': os.path.getsize(file_path) / (1024 * 1024)  # Tamanho em MB
            })
    
    # Ordena por data, mais recente primeiro
    pdfs.sort(key=lambda x: os.path.getmtime(
        os.path.join(pdf_folder, x['url'].split('/')[-1])), 
        reverse=True)
    
    return render_template('posts/pdfs.html', pdfs=pdfs)

@bp.route('/upload_pdf', methods=['POST'])
@login_required
def upload_pdf():
    """Rota específica para upload de PDFs"""
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('posts.upload'))
        
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('posts.upload'))
        
    if not file.filename.lower().endswith('.pdf'):
        flash('Apenas arquivos PDF são permitidos', 'error')
        return redirect(url_for('posts.upload'))
    
    try:
        filename = secure_filename(file.filename)
        unique_filename = f"pdf_{int(time.time())}_{filename}"
        file_path = os.path.join(get_upload_folders()[1], unique_filename)  # PDF_FOLDER
        
        file.save(file_path)
        
        flash('PDF enviado com sucesso!', 'success')
        return redirect(url_for('posts.list_pdfs'))
        
    except Exception as e:
        print(f"Erro no upload do PDF: {str(e)}")
        flash(f'Erro ao fazer upload do PDF: {str(e)}', 'error')
        return redirect(url_for('posts.upload'))

@bp.route('/timeline')
@login_required
def timeline():
    """Timeline personalizada do usuário"""
    page = request.args.get('page', 1, type=int)
    
    # Atualizar a query para incluir o filtro is_hidden
    posts = Post.query\
        .filter_by(is_hidden=False)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10)
    
    return render_template('posts/timeline.html', posts=posts)

@bp.route('/timeline_preferences', methods=['POST'])
@login_required
def save_timeline_preferences():
    """Salva as preferências de timeline do usuário"""
    try:
        sort_by = request.form.get('sort_by', 'recent')
        admin_first = request.form.get('admin_first') == 'true'
        
        # Busca ou cria preferência do usuário
        preference = TimelinePreference.query.filter_by(user_id=current_user.id).first()
        if not preference:
            preference = TimelinePreference(user_id=current_user.id)
            db.session.add(preference)
            
        # Atualiza as preferências
        preference.sort_by = sort_by
        preference.admin_first = admin_first
        
        db.session.commit()
        
        flash('Preferências salvas com sucesso!', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar preferências: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro ao salvar preferências'}), 500 