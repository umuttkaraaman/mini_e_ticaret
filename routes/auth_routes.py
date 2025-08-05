from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('shop.index'))
        else:
            flash('Hatalı giriş bilgisi!', 'danger')

    return render_template('auth/giris.html')

@auth_bp.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')


        try:
            # Kullanıcı sayısını kontrol et
            mevcut_admin_var = User.query.first() is not None
            is_admin = False if mevcut_admin_var else True

            yeni_kullanici = User(
                username=username,
                email=email,
                password=password,
                is_admin=is_admin
            )
            db.session.add(yeni_kullanici)
            db.session.commit()

            flash('Kayıt başarılı. Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.giris'))
        except Exception as e:
            db.session.rollback()
            flash(f'Kayıt sırasında hata oluştu: {str(e)}', 'danger')

    return render_template('auth/kayit.html')



@auth_bp.route('/cikis')
@login_required
def cikis():
    logout_user()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('auth.giris'))
