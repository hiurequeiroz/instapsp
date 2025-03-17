from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc, distinct
from ..models.user import User
from ..models.post import Post
from ..models.comment import Comment
from ..models.like import Like
from ..models.visibility import Visibility
from ..models.timeline_preference import TimelinePreference
from ..extensions import db
from functools import wraps
from markdown import markdown

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado.')
            return redirect(url_for('posts.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def index():
    """Painel de administração"""
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_likes = Like.query.count()
    
    return render_template('admin/index.html',
                         total_users=total_users,
                         total_posts=total_posts,
                         total_comments=total_comments,
                         total_likes=total_likes)

@bp.route('/posts')
@login_required
@admin_required
def posts():
    """Gerenciamento de posts"""
    sort_by = request.args.get('sort', 'recent')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if sort_by == 'likes':
        posts = Post.query\
            .join(Like)\
            .group_by(Post.id)\
            .order_by(func.count(Like.id).desc())
    
    elif sort_by == 'comments':
        posts = Post.query\
            .join(Comment)\
            .group_by(Post.id)\
            .order_by(func.count(Comment.id).desc())
    
    else:  # recent
        posts = Post.query.order_by(Post.created_at.desc())
    
    pagination = posts.paginate(page=page, per_page=per_page)
    
    return render_template('admin/posts.html',
                         posts=pagination.items,
                         pagination=pagination,
                         sort_by=sort_by)

@bp.route('/users')
@login_required
@admin_required
def users():
    """Lista de usuários e suas estatísticas"""
    users = db.session.query(
        User,
        func.count(distinct(Post.id)).label('post_count'),
        func.count(distinct(Comment.id)).label('comment_count'),
        func.count(distinct(Like.id)).label('like_count')
    ).select_from(User)\
    .outerjoin(Post, User.id == Post.user_id)\
    .outerjoin(Comment, User.id == Comment.user_id)\
    .outerjoin(Like, User.id == Like.user_id)\
    .group_by(User.id)\
    .all()
    
    return render_template('admin/users.html', 
                         users=users,
                         sort_options=TimelinePreference.SORT_OPTIONS)

@bp.route('/users/<int:user_id>/timeline-preferences', methods=['POST'])
@login_required
@admin_required
def update_timeline_preferences(user_id):
    """Atualiza as preferências de timeline de um usuário"""
    try:
        user = User.query.get_or_404(user_id)
        sort_by = request.json.get('sort_by')
        
        print(f"Atualizando preferência para usuário {user.id}: {sort_by}")
        
        if sort_by not in TimelinePreference.SORT_OPTIONS:
            return jsonify({'error': 'Opção de ordenação inválida'}), 400
        
        preference = TimelinePreference.query.filter_by(user_id=user_id).first()
        if not preference:
            preference = TimelinePreference(user_id=user_id)
            db.session.add(preference)
        
        preference.sort_by = sort_by
        db.session.commit()
        
        print(f"Preferência atualizada com sucesso: {preference.sort_by}")
        
        return jsonify({
            'success': True,
            'message': 'Preferências atualizadas com sucesso',
            'sort_by': sort_by
        })
    except Exception as e:
        print(f"Erro ao atualizar preferência: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/timeline/<int:user_id>')
@login_required
@admin_required
def user_timeline(user_id):
    """Mostra a timeline de um usuário específico"""
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    return render_template('admin/user_timeline.html', user=user, posts=posts)

@bp.route('/timeline/<int:user_id>/toggle/<int:post_id>', methods=['POST'])
@login_required
@admin_required
def toggle_visibility(user_id, post_id):
    """Alterna a visibilidade de um post para um usuário"""
    visibility = Visibility.query.filter_by(user_id=user_id, post_id=post_id).first()
    
    if visibility:
        visibility.is_visible = not visibility.is_visible
    else:
        visibility = Visibility(user_id=user_id, post_id=post_id, is_visible=False)
        db.session.add(visibility)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'visible': visibility.is_visible
    })

@bp.route('/comments')
@login_required
@admin_required
def moderate_comments():
    """Moderação de comentários"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    comments = Comment.query\
        .join(User, Comment.user_id == User.id)\
        .join(Post, Comment.post_id == Post.id)\
        .order_by(Comment.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return render_template('admin/comments.html', comments=comments)

@bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_comment(comment_id):
    """Marca um comentário como removido"""
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        comment.is_removed = True
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Comentário removido com sucesso',
            'html': comment.html_text
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/comments/<int:comment_id>', methods=['PUT'])
@login_required
@admin_required
def edit_comment(comment_id):
    """Edita um comentário"""
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        new_text = request.json.get('text')
        if not new_text:
            return jsonify({'success': False, 'error': 'Texto não pode estar vazio'}), 400
            
        comment.text = new_text
        # Converte o markdown para HTML
        html_text = markdown(new_text)
        
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Comentário editado com sucesso',
            'text': new_text,
            'html': html_text
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/posts/<int:post_id>/toggle-visibility', methods=['POST'])
@login_required
@admin_required
def toggle_post_visibility(post_id):
    """Alterna a visibilidade global de um post"""
    try:
        post = Post.query.get_or_404(post_id)
        post.is_hidden = not post.is_hidden
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_hidden': post.is_hidden,
            'message': 'Post ' + ('ocultado' if post.is_hidden else 'visível')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500 