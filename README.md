# 🛒 Mini E-Ticaret Uygulaması

Bu proje, Flask kullanılarak geliştirilen basit ama işlevsel bir **mini e-ticaret platformudur**. Kullanıcılar ürünleri görüntüleyebilir, sepetine ekleyip sipariş oluşturabilir. Admin paneli üzerinden ürün ve sipariş yönetimi yapılabilir.

## 🚀 Özellikler

### 👤 Kullanıcı Paneli
- Kayıt ve giriş sistemi (Flask-Login)
- Ürünleri listeleme
- Sepete ürün ekleme/çıkarma
- Sipariş oluşturma
- Sipariş geçmişini görüntüleme
- Sipariş PDF fişi indirme
- Sipariş iptali (sadece hazırlanıyor durumundakiler)

### 🛠️ Admin Paneli
- Ürün ekleme, düzenleme ve silme
- Tüm kullanıcı siparişlerini listeleme
- Sipariş durumunu güncelleme (Hazırlanıyor, Kargoda, Teslim Edildi)
- Sipariş iptali (Teslim Edildi olanlar hariç)
- Sipariş işlem geçmişi (log) görüntüleme
- Bootstrap ile modern ve responsive arayüz

## 🖥️ Kullanılan Teknolojiler

- Python & Flask
- Flask-Login
- SQLAlchemy (ORM)
- MySQL (MAMP ile bağlantılı)
- Bootstrap 5.3
- ReportLab (PDF çıktısı için)
- HTML / Jinja2 / CSS

## 🏁 Kurulum

```bash
git clone https://github.com/umuttkaraaman/mini_e_ticaret.git
cd mini_e_ticaret
python -m venv venv
source venv/bin/activate  # Windows ise: venv\Scripts\activate
pip install -r requirements.txt
```

> **MAMP kullananlar için:** `app.py` veya `config.py` içindeki MySQL bağlantısını kendine göre düzenle:  
> `mysql+pymysql://root:root@localhost:8889/veritabani_adi`

## ⚙️ Veritabanı Kurulumu

```python
from app import db
db.create_all()
```

## 📂 Proje Yapısı

```
mini_e_ticaret/
├── static/
├── templates/
├── models.py
├── routes/
│   ├── admin_routes.py
│   └── shop_routes.py
├── utils/
│   └── pdf_helper.py
├── app.py
└── README.md
```

## 🔐 Giriş Bilgileri (örnek)

İlk kayıt olan kullanıcı `admin` olarak belirlenir. Diğer kullanıcılar `normal kullanıcı` olur.

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.

## ✍️ Geliştirici

- 👨‍💻 Umut Karaman – [GitHub](https://github.com/umuttkaraaman)