from ..extensions import db
from datetime import datetime

class TimelinePreference(db.Model):
    """Preferências de timeline para cada usuário"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    sort_by = db.Column(db.String(20), default='recent')  # recent, likes, comments, admin_first
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relação com o usuário
    user = db.relationship('User', backref=db.backref('timeline_preference', uselist=False))

    SORT_OPTIONS = {
        'recent': 'Mais recentes primeiro',
        'likes': 'Mais curtidas primeiro',
        'comments': 'Mais comentados primeiro',
        'admin_first': 'Posts de administradores primeiro'
    }

    def __repr__(self):
        return f'<TimelinePreference {self.user_id}>' 