from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from ..models.user import User
from ..email import send_password_reset_email
from flask_mail import Message
import secrets

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rota para registro de novos usuários"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Nome de usuário já existe')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registro realizado com sucesso!')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para login de usuários"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('posts.index'))
            
        flash('Usuário ou senha inválidos')
        
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Rota para logout de usuários"""
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Rota para solicitar reset de senha"""
    if current_user.is_authenticated:
        return redirect(url_for('posts.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        reset_code = request.form.get('reset_code')
        
        user = User.query.filter_by(username=username).first()
        if user and user.verify_reset_code(reset_code):
            return redirect(url_for('auth.reset_password', username=username, code=reset_code))
            
        flash('Código de reset inválido ou expirado')
        return redirect(url_for('auth.reset_password_request'))
    
    return render_template('auth/reset_password_request.html')

@bp.route('/reset_password/<username>/<code>', methods=['GET', 'POST'])
def reset_password(username, code):
    """Rota para resetar a senha usando o código"""
    if current_user.is_authenticated:
        return redirect(url_for('posts.index'))
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_reset_code(code):
        flash('Código de reset inválido ou expirado')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        user.password_hash = generate_password_hash(password)
        user.clear_reset_code()
        db.session.commit()
        flash('Sua senha foi alterada com sucesso')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')

@bp.route('/reset-password', methods=['GET', 'POST'])
def request_password_reset():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = secrets.token_urlsafe(32)
            # Salvar token no banco de dados
            # Enviar email com link de recuperação
            flash('Se o email existir em nossa base de dados, você receberá instruções para recuperar sua senha.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html') 