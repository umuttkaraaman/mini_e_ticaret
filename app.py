from flask import Flask, redirect, url_for
from extensions import db
from flask_migrate import Migrate
from flask_login import LoginManager
from models import User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Veritabanı ve login ayarları
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'auth.giris'  # Giriş yapılmadan erişim isteyenler buraya yönlendirilir
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprint'leri import et ve kaydet
from routes.auth_routes import auth_bp
from routes.shop_routes import shop_bp
from routes.admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(admin_bp)

# Giriş ekranını ana sayfa yap
@app.route('/')
def anasayfa():
    return redirect(url_for('auth.giris'))

# Uygulama çalıştır
if __name__ == '__main__':
    app.run(debug=True)
