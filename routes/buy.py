from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from app_models import Product, Purchase, Basket, User  # User eklendi

buy_bp = Blueprint('buy', __name__)

# Satın Alma İşlemi
@buy_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    current_user = get_jwt_identity()
    user = User.query.get(int(current_user))  # Kullanıcıyı al
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    basket = data.get("basket", [])

    if not basket:
        return jsonify({"error": "Basket is empty"}), 400

    # Sepet ürünlerini satın al
    for item in basket:
        product_id = item["product_id"]
        quantity = item["quantity"]
        product = Product.query.get(product_id)

        if not product or product.stock < quantity:
            return jsonify({"error": f"Product {product_id} not available or insufficient stock"}), 400

        # Purchase kaydı
        purchase = Purchase(
            user_id=user.id,
            product_id=product_id,
            quantity=quantity
        )
        product.stock -= quantity  # Stok güncellemesi
        db.session.add(purchase)

    db.session.commit()

    return jsonify({"message": "Checkout successful, products purchased!"}), 200
