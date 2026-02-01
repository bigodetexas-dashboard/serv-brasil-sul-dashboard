"""
Discord OAuth Integration
"""
import os
import requests
from functools import wraps
from flask import session, redirect, url_for, request

DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'https://bigodetexas-dashboard.onrender.com/callback')

DISCORD_API_BASE = 'https://discord.com/api/v10'
DISCORD_OAUTH_URL = f'{DISCORD_API_BASE}/oauth2/authorize'
DISCORD_TOKEN_URL = f'{DISCORD_API_BASE}/oauth2/token'
DISCORD_USER_URL = f'{DISCORD_API_BASE}/users/@me'

def get_oauth_url():
    """Gera URL de autenticação do Discord"""
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify email'
    }
    return f"{DISCORD_OAUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

def exchange_code(code):
    """Troca o código por um token de acesso"""
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(DISCORD_TOKEN_URL, data=data, headers=headers)
    return response.json()

def get_user_info(access_token):
    """Busca informações do usuário"""
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(DISCORD_USER_URL, headers=headers)
    return response.json()

def login_required(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
