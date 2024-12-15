import os
from flask import Flask
from flask_migrate import Migrate
from extensions import initialize_extensions  # extensions.py'deki initialize_extensions fonksiyonu
from flask_cors import CORS  # CORS izinleri için
from flask_jwt_extended import JWTManager  # JWT için
from extensions import db  # db'yi extensions.py dosyasından al
from datetime import timedelta

# Flask uygulamasını oluşturma
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ecommerce.db')  # Veritabanı URL'si
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')  # JWT Secret Key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# CORS izinlerini başlat
CORS(app)

# JWT Manager'ı başlat
jwt = JWTManager(app)

# Migrate'yi başlat
migrate = Migrate(app, db)

# Gerekli uzantıları başlatma
initialize_extensions(app)

# Modelleri ve rotaları yükleme
from app_models import *  # Modelleri import et
from routes.products import products_bp
from routes.basket import basket_bp  # basket_bp'yi import et
from routes.checkout import checkout_bp  # checkout_bp'yi import et
from routes.buy import buy_bp  # buy_bp'yi import et
from routes.profile import profile_bp  # profile_bp'yi import et

# Blueprint'leri kaydetme
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(basket_bp, url_prefix='/basket')
app.register_blueprint(checkout_bp, url_prefix='/checkout')
app.register_blueprint(buy_bp, url_prefix='/buy')
app.register_blueprint(profile_bp, url_prefix="/profile")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Veritabanı tablolarını oluştur
    app.run(host='0.0.0.0', port=5000, debug=True)
