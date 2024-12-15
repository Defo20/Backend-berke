import os
from flask import Flask
from flask_migrate import Migrate
from extensions import initialize_extensions
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from extensions import db
from datetime import timedelta

# Flask uygulamasını oluşturma
app = Flask(__name__)

# Veritabanı bağlantısını ortam değişkeninden al
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',  # Ortam değişkeninden al
    'sqlite:///ecommerce.db'  # Yedek olarak SQLite kullan
)

# Diğer ayarlar
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Gerekli uzantıları başlatma
CORS(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
initialize_extensions(app)

# Modelleri ve blueprint'leri ekleme
from app_models import *
from routes.products import products_bp
from routes.basket import basket_bp
from routes.checkout import checkout_bp
from routes.buy import buy_bp
from routes.profile import profile_bp

app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(basket_bp, url_prefix='/basket')
app.register_blueprint(checkout_bp, url_prefix='/checkout')
app.register_blueprint(buy_bp, url_prefix='/buy')
app.register_blueprint(profile_bp, url_prefix="/profile")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
