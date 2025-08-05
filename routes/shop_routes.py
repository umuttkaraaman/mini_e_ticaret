from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import Product, CartItem, Order, OrderItem
from flask import send_file, abort
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


shop_bp = Blueprint('shop', __name__)

# Ana sayfa: Ürün kataloğu
@shop_bp.route('/')
def index():
    urunler = Product.query.all()
    return render_template('shop/index.html', urunler=urunler)

# Ürünü sepete ekle
@shop_bp.route('/sepete_ekle/<int:urun_id>', methods=["POST", "GET"])
@login_required
def sepete_ekle(urun_id):
    urun = Product.query.get_or_404(urun_id)

    # Aynı ürün sepette varsa adetini artır
    mevcut = CartItem.query.filter_by(user_id=current_user.id, product_id=urun.id).first()
    if mevcut:
        mevcut.quantity += 1
    else:
        yeni_urun = CartItem(user_id=current_user.id, product_id=urun.id, quantity=1)
        db.session.add(yeni_urun)

    db.session.commit()
    flash(f"{urun.name} sepete eklendi!", "success")
    return redirect(url_for('shop.index'))

# Sepeti görüntüle
@shop_bp.route('/sepetim')
@login_required
def sepetim():
    sepet = CartItem.query.filter_by(user_id=current_user.id).all()
    toplam = sum(item.product.price * item.quantity for item in sepet)
    return render_template('shop/sepet.html', sepet=sepet, toplam=toplam)

# Sepetten ürün çıkar
@shop_bp.route('/sepetten_cikar/<int:item_id>')
@login_required
def sepetten_cikar(item_id):
    item = CartItem.query.get_or_404(item_id)

    if item.user_id != current_user.id:
        flash("Yetkisiz işlem!", "danger")
        return redirect(url_for('shop.sepetim'))

    db.session.delete(item)
    db.session.commit()
    flash("Ürün sepetten çıkarıldı.", "info")
    return redirect(url_for('shop.sepetim'))

# Sepette ürün miktarını artır
@shop_bp.route('/sepet_arttir/<int:item_id>')
@login_required
def sepet_arttir(item_id):
    item = CartItem.query.get_or_404(item_id)

    if item.user_id != current_user.id:
        flash("Yetkisiz işlem!", "danger")
        return redirect(url_for('shop.sepetim'))

    item.quantity += 1
    db.session.commit()
    return redirect(url_for('shop.sepetim'))

# Sepette ürün miktarını azalt
@shop_bp.route('/sepet_azalt/<int:item_id>')
@login_required
def sepet_azalt(item_id):
    item = CartItem.query.get_or_404(item_id)

    if item.user_id != current_user.id:
        flash("Yetkisiz işlem!", "danger")
        return redirect(url_for('shop.sepetim'))

    if item.quantity > 1:
        item.quantity -= 1
    else:
        db.session.delete(item)

    db.session.commit()
    return redirect(url_for('shop.sepetim'))

# Siparişi tamamla
@shop_bp.route('/siparis_ver')
@login_required
def siparis_ver():
    sepet = CartItem.query.filter_by(user_id=current_user.id).all()

    if not sepet:
        flash("Sepetiniz boş.", "warning")
        return redirect(url_for('shop.index'))

    toplam_fiyat = sum(item.product.price * item.quantity for item in sepet)

    # Sipariş oluştur
    yeni_siparis = Order(user_id=current_user.id, total_price=toplam_fiyat)
    db.session.add(yeni_siparis)
    db.session.commit()

    for item in sepet:
        siparis_ogesi = OrderItem(
            order_id=yeni_siparis.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )

        # Stok düşür
        urun = Product.query.get(item.product_id)
        if urun.stock >= item.quantity:
            urun.stock -= item.quantity
        else:
            flash(f"{urun.name} için yeterli stok yok!", "danger")
            return redirect(url_for('shop.sepetim'))

        db.session.add(siparis_ogesi)
        db.session.delete(item)

    db.session.commit()
    flash("Sipariş başarıyla oluşturuldu!", "success")
    return redirect(url_for('shop.index'))

# Kullanıcının siparişlerini görüntüle
@shop_bp.route("/siparislerim")
@login_required
def siparislerim():
    if current_user.is_admin:
        flash("Admin hesabı sipariş görüntüleyemez.", "warning")
        return redirect(url_for("shop.index"))

    siparisler = Order.query.filter_by(user_id=current_user.id).all()
    return render_template("shop/siparislerim.html", siparisler=siparisler)

@shop_bp.route("/siparis_iptal/<int:siparis_id>")
@login_required
def siparis_iptal(siparis_id):
    siparis = Order.query.get_or_404(siparis_id)

    if siparis.user_id != current_user.id:
        flash("Bu siparişi iptal etmeye yetkiniz yok.", "danger")
        return redirect(url_for("shop.siparislerim"))

    if siparis.status != 'Hazırlanıyor':
        flash("Sadece 'Hazırlanıyor' durumundaki siparişleri iptal edebilirsiniz.", "warning")
        return redirect(url_for("shop.siparislerim"))

    # Stokları geri yükle
    for item in siparis.order_items:
        item.product.stock += item.quantity

    # Sipariş ve içeriklerini sil
    for item in siparis.order_items:
        db.session.delete(item)
    db.session.delete(siparis)

    # 🔥 Burada log ekle
    from models import SiparisLog  # üstte import etmediysen burada et
    log = SiparisLog(
        user_id=current_user.id,
        siparis_id=siparis.id,
        islem='Sipariş İptal Edildi'
    )
    db.session.add(log)

    db.session.commit()
    flash("Sipariş başarıyla iptal edildi. Ürünler stoğa geri yüklendi.", "info")
    return redirect(url_for("shop.siparislerim"))



@shop_bp.route("/siparis_detay/<int:siparis_id>")
@login_required
def siparis_detay(siparis_id):
    siparis = Order.query.get_or_404(siparis_id)
    if siparis.user_id != current_user.id and not current_user.is_admin:
        flash("Bu siparişi görüntüleyemezsiniz.", "danger")
        return redirect(url_for("shop.index"))

    return render_template("shop/siparis_detay.html", siparis=siparis)

def pdf_olustur(siparis):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os
    from flask import current_app
    from io import BytesIO

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Fontu doğru yoldan yükle
    font_path = os.path.join(current_app.root_path, 'static', 'fonts', 'DejaVuSans.ttf')
    pdfmetrics.registerFont(TTFont('DejaVu', font_path))
    pdf.setFont("DejaVu", 12)

    y = height - 50
    pdf.drawString(50, y, f"Sipariş No: {siparis.id}")
    y -= 25
    pdf.drawString(50, y, f"Tarih: {siparis.created_at.strftime('%d.%m.%Y %H:%M')}")
    y -= 25
    pdf.drawString(50, y, f"Toplam Tutar: ₺{siparis.total_price}")
    y -= 40
    pdf.drawString(50, y, "Ürünler:")
    y -= 25

    for item in siparis.order_items:
        pdf.drawString(60, y, f"- {item.product.name} x {item.quantity} adet (₺{item.price})")
        y -= 20
        if y < 100:
            pdf.showPage()
            pdf.setFont("DejaVu", 12)
            y = height - 50

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer


@shop_bp.route("/kullanici/siparis/<int:siparis_id>/pdf")
@login_required
def kullanici_siparis_pdf(siparis_id):
    siparis = Order.query.get_or_404(siparis_id)
    if siparis.user_id != current_user.id:
        abort(403)

    pdf = pdf_olustur(siparis)  # bu fonksiyon önceden tanımlı olmalı
    return send_file(pdf, as_attachment=True, download_name=f"siparis_{siparis.id}.pdf", mimetype='application/pdf')


