from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import Product, Order, OrderItem, SiparisLog  # ✅ Eksik import eklendi
from utils.pdf_helper import pdf_olustur
from flask import send_file

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_kontrol():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash("Bu sayfaya erişim yetkiniz yok!", "danger")
        return False
    return True

@admin_bp.route('/urunler')
@login_required
def urun_listesi():
    if not admin_kontrol():
        return redirect(url_for('shop.index'))

    urunler = Product.query.all()
    return render_template('admin/urunler.html', urunler=urunler)

@admin_bp.route('/urun/ekle', methods=['GET', 'POST'])
@login_required
def urun_ekle():
    if not admin_kontrol():
        return redirect(url_for('shop.index'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        image_url = request.form['image_url']

        yeni_urun = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image_url=image_url
        )
        db.session.add(yeni_urun)
        db.session.commit()
        flash("Ürün başarıyla eklendi.", "success")
        return redirect(url_for('admin.urun_listesi'))

    return render_template('admin/urun_ekle.html')

@admin_bp.route('/urun/sil/<int:urun_id>')
@login_required
def urun_sil(urun_id):
    if not admin_kontrol():
        return redirect(url_for('shop.index'))

    urun = Product.query.get_or_404(urun_id)
    db.session.delete(urun)
    db.session.commit()
    flash("Ürün başarıyla silindi.", "info")
    return redirect(url_for('admin.urun_listesi'))

@admin_bp.route('/urun/<int:urun_id>/duzenle', methods=['GET', 'POST'])
@login_required
def urun_duzenle(urun_id):
    if not admin_kontrol():
        return redirect(url_for('shop.index'))

    urun = Product.query.get_or_404(urun_id)

    if request.method == 'POST':
        urun.name = request.form['name']
        urun.description = request.form['description']
        urun.price = float(request.form['price'])
        urun.stock = int(request.form['stock'])
        urun.image_url = request.form['image_url']

        db.session.commit()
        flash("Ürün başarıyla güncellendi.", "success")
        return redirect(url_for('admin.urun_listesi'))

    return render_template('admin/urun_duzenle.html', urun=urun)

@admin_bp.route('/tum_siparisler')
@login_required
def tum_siparisler():
    if not admin_kontrol():
        return redirect(url_for('shop.index'))

    siparisler = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/tum_siparisler.html', siparisler=siparisler)

@admin_bp.route('/siparis/iptal/<int:siparis_id>', methods=['POST'])
@login_required
def siparis_iptal(siparis_id):
    if not current_user.is_admin:
        flash("Bu işlem sadece admin kullanıcılar içindir.", "danger")
        return redirect(url_for("shop.index"))

    siparis = Order.query.get_or_404(siparis_id)

    if siparis.status == "Teslim Edildi":
        flash("Teslim edilen sipariş iptal edilemez!", "warning")
        return redirect(url_for("admin.tum_siparisler"))

    # Sipariş iptali işlemleri buraya gelecek (stok geri yükleme vs.)
    flash("Sipariş başarıyla iptal edildi.", "success")
    return redirect(url_for("admin.tum_siparisler"))


@admin_bp.route('/siparis_durum_guncelle/<int:siparis_id>', methods=['POST'])
@login_required
def siparis_durum_guncelle(siparis_id):
    if not current_user.is_admin:
        flash("Bu işlem sadece admin kullanıcılar içindir.", "danger")
        return redirect(url_for("shop.index"))

    yeni_durum = request.form.get('yeni_durum')
    siparis = Order.query.get_or_404(siparis_id)

    eski_durum = siparis.status  # Güncellemeden önceki durumu al
    siparis.status = yeni_durum
    db.session.commit()

    # Eğer yeni durum "Teslim Edildi" ise logla
    if yeni_durum == "Teslim Edildi":
        from models import SiparisLog  # İçe aktarma yoksa en üste ekle
        log = SiparisLog(
            user_id=current_user.id,
            siparis_id=siparis.id,
            islem=f"Sipariş 'Teslim Edildi' olarak güncellendi"
        )
        db.session.add(log)
        db.session.commit()

    flash("Sipariş durumu başarıyla güncellendi.", "success")
    return redirect(url_for('admin.tum_siparisler'))


@admin_bp.route('/siparis_loglari')
@login_required
def siparis_loglari():
    if not admin_kontrol():
        return redirect(url_for('shop.index'))

    loglar = SiparisLog.query.order_by(SiparisLog.zaman.desc()).all()
    return render_template('admin/siparis_loglari.html', loglar=loglar)

@admin_bp.route('/siparis/<int:siparis_id>/pdf')
@login_required
def siparis_pdf(siparis_id):
    siparis = Order.query.get_or_404(siparis_id)

    if not current_user.is_admin and current_user.id != siparis.user_id:
        flash("Bu işlem için yetkiniz yok.", "danger")
        return redirect(url_for("shop.index"))

    pdf = pdf_olustur(siparis)
    return send_file(pdf, as_attachment=True, download_name=f"siparis_{siparis.id}_fis.pdf", mimetype='application/pdf')
