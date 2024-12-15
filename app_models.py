from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # "user" veya "seller"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Kullanıcı oluşturulma tarihi
    phone = db.Column(db.String(15), nullable=True)
    profile_photo = db.Column(db.String(255), nullable=True)

    # İlişkiler
    products = db.relationship('Product', backref='seller', lazy=True)  # Satıcı ürün ilişkisi
    purchases = db.relationship('Purchase', backref='user', lazy=True)  # Kullanıcı satın alma ilişkisi


class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(255))  # Ürün görsel URL'si
    description = db.Column(db.Text)  # Ürün açıklaması
    is_featured = db.Column(db.Boolean, default=False)  # Öne çıkarılmış ürün bayrağı
    is_active = db.Column(db.Boolean, default=True)  # Ürün aktif mi? (yeni sütun)
    discounted_price = db.Column(db.Float)  # İndirimli fiyat
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Ürün eklenme tarihi

    # İlişkiler
    purchases = db.relationship('Purchase', backref='product', lazy=True)
    basket_items = db.relationship('Basket', backref='associated_product', cascade="all, delete-orphan")  # backref uyumu sağlandı



class Purchase(db.Model):
    __tablename__ = 'purchase'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)  # Satın alma tarihi
    quantity = db.Column(db.Integer, nullable=False)  # Satın alınan miktar

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plan'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Plan adı (Free, Premium, Gold)
    price = db.Column(db.Float, nullable=False)  # Aylık ücret
    description = db.Column(db.String(255))  # Plan açıklaması


class SellerSubscription(db.Model):
    __tablename__ = 'seller_subscription'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Satıcı kimliği
    subscription_plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plan.id'), nullable=False)  # Abonelik planı
    start_date = db.Column(db.DateTime, default=datetime.utcnow)  # Abonelik başlangıç tarihi
    end_date = db.Column(db.DateTime)  # Abonelik bitiş tarihi
    is_active = db.Column(db.Boolean, default=True)  # Abonelik durumu

class Basket(db.Model):
    __tablename__ = 'basket'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # İlişkiler
    user = db.relationship('User', backref=db.backref('basket_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('basket_associations', lazy=True))  # backref adı değiştirildi