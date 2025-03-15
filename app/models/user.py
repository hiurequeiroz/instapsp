from flask_login import UserMixin
from ..extensions import db, login_manager
import secrets
import datetime

class User(UserMixin, db.Model):
    """Modelo para usuários"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    reset_code = db.Column(db.String(8), unique=True, nullable=True)
    reset_code_expiry = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    # A relação já está definida no TimelinePreference através do backref
    # timeline_preference = db.relationship('TimelinePreference', backref='user', uselist=False)

    def generate_reset_code(self):
        """Gera um código de 8 caracteres para reset de senha"""
        self.reset_code = secrets.token_hex(4)  # 8 caracteres
        self.reset_code_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        db.session.commit()
        return self.reset_code

    def verify_reset_code(self, code):
        """Verifica se o código é válido e não expirou"""
        if not self.reset_code or not self.reset_code_expiry:
            return False
        if self.reset_code != code:
            return False
        if datetime.datetime.utcnow() > self.reset_code_expiry:
            return False
        return True

    def clear_reset_code(self):
        """Limpa o código de reset após uso"""
        self.reset_code = None
        self.reset_code_expiry = None
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 