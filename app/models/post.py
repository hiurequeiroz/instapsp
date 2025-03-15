from datetime import datetime
from ..extensions import db
from .like import Like
from .visibility import Visibility

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

    def __repr__(self):
        return f'<Post {self.id}>'

    def is_liked_by(self, user):
        """Verifica se o post foi curtido pelo usuário"""
        return Like.query.filter_by(user_id=user.id, post_id=self.id).first() is not None

    def like_count(self):
        """Retorna o número de curtidas do post"""
        return Like.query.filter_by(post_id=self.id).count()

    def is_visible_to(self, user):
        """Verifica se o post é visível para o usuário"""
        visibility = Visibility.query.filter_by(post_id=self.id, user_id=user.id).first()
        return visibility.is_visible if visibility else True  # Visível por padrão 