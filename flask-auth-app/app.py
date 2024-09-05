import os
import json

from authlib.integrations.base_client.errors import OAuthError
from flask import Flask, redirect, url_for, session, request
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required


# โหลดข้อมูลจากไฟล์ JSON
with open('flask-auth-app/client_secret_744419703652-c0f3gm09a771ur4aotfnhs471glghuus.apps.googleusercontent.com.json', 'r') as f:
    client_secrets = json.load(f)

client_id = client_secrets['web']['client_id']
client_secret = client_secrets['web']['client_secret']
auth_uri = client_secrets['web']['auth_uri']
token_uri = client_secrets['web']['token_uri']
auth_provider_x509_cert_url = client_secrets['web']['auth_provider_x509_cert_url']
redirect_uri = client_secrets['web']['redirect_uris'][0]  # สมมติใช้ตัวแรกในรายการ

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")  # ควรเก็บไว้ใน environment variable

oauth = OAuth(app)
login_manager = LoginManager(app)

# ตั้งค่า Google OAuth
google = oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID", client_id),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", client_secret),
    access_token_url=token_uri,
    access_token_params=None,
    authorize_url=auth_uri,
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs', 
    client_kwargs={'scope': 'openid email profile'},
)

# ตั้งค่า Apple OAuth
apple = oauth.register(
    name='apple',
    client_id=os.environ.get("APPLE_CLIENT_ID"),
    client_secret=os.environ.get("APPLE_CLIENT_SECRET"),
    access_token_url='https://appleid.apple.com/auth/token',
    authorize_url='https://appleid.apple.com/auth/authorize',
    api_base_url='https://appleid.apple.com/',
    client_kwargs={
        'scope': 'name email',
        'response_mode': 'form_post'
    },
)

class User(UserMixin):
    def __init__(self, id, email, name=None, phone=None):
        self.id = id
        self.email = email
        self.name = name
        self.phone = phone

@login_manager.user_loader
def load_user(user_id):
    # ในที่นี้ควรดึงข้อมูลจากฐานข้อมูลจริง
    return User(user_id, f"{user_id}@example.com")

@app.route('/')
def index():
    return 'Welcome to the app!'

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('google_auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_auth():
    try:
        token = google.authorize_access_token()
        if token is None:
                print('Failed to authorize with Google. Please try again.', 'error')
                return redirect(url_for('login_google'))
        resp = google.get('userinfo')
        user_info = resp.json()
        user = User(user_info['id'], user_info['email'], user_info.get('name'))
        print(user.email, user.name)
        login_user(user)
        return redirect(url_for('index'))
    except OAuthError as e:
        # จัดการข้อผิดพลาดที่เกิดจากการปฏิเสธการอนุญาต
        if e.error == 'access_denied':
            print('Authorization was denied by the user. Please try again.', 'error')
        else:
            print(f'An error occurred: {str(e.error)}', 'error')
        return redirect(url_for('login_google'))

    except Exception as e:
        # จัดการข้อผิดพลาดอื่น ๆ ที่ไม่คาดคิด
        print(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('login_google'))

@app.route('/login/apple')
def login_apple():
    redirect_uri = url_for('apple_auth', _external=True)
    return apple.authorize_redirect(redirect_uri)

@app.route('/login/apple/callback', methods=['GET', 'POST'])
def apple_auth():
    token = apple.authorize_access_token()
    # Apple returns user data in the ID token
    id_token = token.get('id_token')
    # You need to decode and verify the ID token
    # This step requires additional libraries and is more complex
    # For simplicity, we'll assume we have the user data
    user_info = {'id': 'apple_user_id', 'email': 'user@example.com'}
    user = User(user_info['id'], user_info['email'])
    
    login_user(user)
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)