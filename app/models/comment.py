from datetime import datetime
from ..extensions import db
import re

class Comment(db.Model):
    """Modelo para comentários em posts"""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    is_removed = db.Column(db.Boolean, default=False)
    
    author = db.relationship('User', backref='comments')

    @property
    def html_text(self):
        """Retorna o texto do comentário formatado como HTML"""
        if self.is_removed:
            return '<em><i class="fas fa-exclamation-circle"></i> Comentário removido pelo administrador</em>'
        if not self.text:
            return ''
            
        text = self.text
        # Processa texto riscado (~~texto~~)
        text = re.sub(r'~~(.*?)~~', r'<del>\1</del>', text)
        # Processa negrito (**texto**)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        # Processa itálico (_texto_)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
        # Processa sublinhado (__texto__)
        text = re.sub(r'__(.*?)__', r'<u>\1</u>', text)
        
        return text 