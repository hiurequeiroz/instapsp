from datetime import datetime
from ..extensions import db

class Tag(db.Model):
    """Modelo para marcações de usuários em posts"""
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Garante que um usuário só pode ser marcado uma vez em cada post
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_post_user_tag'),) 