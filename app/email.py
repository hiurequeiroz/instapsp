from flask_mail import Message
from flask import render_template, current_app
from . import mail

def send_password_reset_email(user):
    """Envia email com link para reset de senha"""
    token = user.get_reset_password_token()
    send_email(
        'Reset de Senha',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt',
                                user=user, token=token),
        html_body=render_template('email/reset_password.html',
                                user=user, token=token)
    )

def send_email(subject, sender, recipients, text_body, html_body):
    """Função auxiliar para enviar emails"""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg) 