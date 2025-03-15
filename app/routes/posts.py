from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from ..extensions import db
from ..models.post import Post
from ..models.comment import Comment
from ..utils.image_handler import process_image
import time
from ..models.like import Like
from ..models.user import User
from ..models.tag import Tag
from ..models.visibility import Visibility
from ..models.timeline_preference import TimelinePreference
from sqlalchemy import func

bp = Blueprint('posts', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
@login_required
def index():
    """Página inicial com feed de fotos"""
    preference = TimelinePreference.query.filter_by(user_id=current_user.id).first()
    sort_by = preference.sort_by if preference else 'recent'
    
    # Query base
    query = Post.query\
        .outerjoin(Visibility, 
                  (Visibility.post_id == Post.id) & 
                  (Visibility.user_id == current_user.id))\
        .filter((Visibility.is_visible == True) | 
                (Visibility.id == None))
    
    if sort_by == 'likes':
        # Ordenar por número de curtidas
        query = query.outerjoin(Like)\
            .group_by(Post.id)\
            .order_by(func.count(Like.id).desc(), Post.created_at.desc())
    elif sort_by == 'comments':
        # Ordenar por número de comentários
        query = query.outerjoin(Comment)\
            .group_by(Post.id)\
            .order_by(func.count(Comment.id).desc(), Post.created_at.desc())
    elif sort_by == 'admin_first':
        # Posts de administradores primeiro
        query = query.join(User, Post.user_id == User.id)\
            .order_by(User.is_admin.desc(), Post.created_at.desc())
    else:  # recent
        query = query.order_by(Post.created_at.desc())
    
    # Adicionar logs para debug
    print(f"Preferência do usuário: {sort_by}")
    print(f"SQL Query: {query}")
    
    page = request.args.get('page', 1, type=int)
    
    posts = query.paginate(page=page, per_page=10)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('posts/_posts_list.html', posts=posts)
    
    return render_template('posts/index.html', posts=posts)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('posts/upload.html')
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
            
        # Processa a imagem com o filtro selecionado
        filter_name = request.form.get('filter', 'normal')
        processed_image = process_image(file, filter_name)
            
        # Cria o diretório de uploads se não existir
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Gera um nome único para o arquivo
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{int(time.time())}.jpg"  # Sempre salva como JPG após processamento
        filepath = os.path.join(upload_folder, filename)
        
        # Salva o arquivo processado
        with open(filepath, 'wb') as f:
            f.write(processed_image.getvalue())
        
        # Cria o post no banco de dados
        post = Post(
            image_path=filename,  # Salvamos apenas o nome do arquivo
            caption=request.form.get('caption', ''),
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Imagem enviada com sucesso!'
        })
        
    except Exception as e:
        print(f"Erro no upload: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': f'Erro ao fazer upload: {str(e)}'
        }), 500

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
    
    return redirect(url_for('posts.index'))

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