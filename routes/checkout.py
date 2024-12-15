from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from app_models import Purchase, Basket, Product, User

checkout_bp = Blueprint('checkout', __name__)

# 1. Ödeme ve Satın Alma İşlemi
@checkout_bp.route('', methods=['POST'])
@jwt_required()
def process_checkout():
    current_user_id = get_jwt_identity()

    # Kullanıcıyı doğrula
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "Kullanıcı bulunamadı."}), 404

    # Kullanıcının sepetindeki ürünleri al
    basket_items = Basket.query.filter_by(user_id=current_user_id).all()
    if not basket_items:
        return jsonify({"error": "Sepetiniz boş."}), 400

    # Ödeme için gerekli bilgiler
    data = request.json
    name = data.get("name")
    phone = data.get("phone")
    address = data.get("address")

    if not (name and phone and address):
        return jsonify({"error": "Lütfen ödeme bilgilerini eksiksiz girin."}), 400

    # Rol tabanlı erişim kontrolü: Admin veya kullanıcı işlem yapabilir
    if user.role not in ["admin", "user"]:
        return jsonify({"error": "Bu işlemi gerçekleştirme yetkiniz yok."}), 403

    # Sepetteki her ürün için satın alma işlemi oluştur
    total_price = 0
    insufficient_stock_products = []

    for item in basket_items:
        product = Product.query.get(item.product_id)
        if not product:
            return jsonify({"error": f"Ürün ID {item.product_id} bulunamadı."}), 404

        # Stok kontrolü
        if product.stock < item.quantity:
            insufficient_stock_products.append({"name": product.name, "stock": product.stock})
            continue

        # Satın alma kaydını oluştur
        purchase = Purchase(
            user_id=current_user_id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.session.add(purchase)

        # Ürünün stok miktarını güncelle
        product.stock -= item.quantity
        total_price += product.price * item.quantity

    # Eğer yetersiz stoklu ürünler varsa
    if insufficient_stock_products:
        return jsonify({
            "error": "Bazı ürünlerde yeterli stok yok.",
            "details": insufficient_stock_products
        }), 400

    # Sepeti sıfırla
    db.session.query(Basket).filter_by(user_id=current_user_id).delete()

    # Veritabanı işlemlerini commit et
    db.session.commit()

    return jsonify({
        "message": f"Ödeme başarılı! Toplam tutar: {total_price}₺. Siparişiniz başarıyla tamamlandı."
    }), 200
