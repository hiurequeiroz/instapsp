from datetime import datetime
from ..extensions import db
from .like import Like
from .visibility import Visibility
from flask import url_for

class Post(db.Model):
    """Modelo para posts de fotos"""
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(150), nullable=False)
    caption = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True, order_by='Comment.created_at')
    likes = db.relationship('Like', backref='post', lazy=True)
    tagged_users = db.relationship('User', secondary='tag', backref='tagged_in')
    visibilities = db.relationship('Visibility', backref='post', lazy=True)
    is_hidden = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Post {self.id}>'

    def is_liked_by(self, user):
        """Verifica se o post foi curtido pelo usuário"""
        if not user.is_authenticated:
            return False
        return Like.query.filter_by(user_id=user.id, post_id=self.id).first() is not None

    def like_count(self):
        """Retorna o número de curtidas do post"""
        return Like.query.filter_by(post_id=self.id).count()

    def is_visible_to(self, user):
        """Verifica se o post é visível para o usuário"""
        visibility = Visibility.query.filter_by(post_id=self.id, user_id=user.id).first()
        return visibility.is_visible if visibility else True  # Visível por padrão 

    @property
    def image_url(self):
        """Retorna a URL completa da imagem"""
        if self.image_path:
            # Garante que o caminho comece com 'uploads/'
            path = self.image_path if self.image_path.startswith('uploads/') else f'uploads/{self.image_path}'
            return url_for('static', filename=path)
        return None 