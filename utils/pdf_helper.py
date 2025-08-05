from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

def pdf_olustur(siparis):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 12)

    c.drawString(100, 800, f"Siparis Fisi - Siparis ID: {siparis.id}")
    c.drawString(100, 780, f"Kullanici: {siparis.user.username}")
    c.drawString(100, 760, f"Tarih: {siparis.created_at.strftime('%d.%m.%Y %H:%M')}")
    c.drawString(100, 740, f"Durum: {siparis.status}")
    c.drawString(100, 720, "Urunler:")

    y = 700
    for item in siparis.order_items:
        c.drawString(120, y, f"- {item.product.name} ({item.quantity} adet) - ₺{item.price}")
        y -= 20

    c.drawString(100, y - 20, f"Toplam Tutar: ₺{siparis.total_price}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
