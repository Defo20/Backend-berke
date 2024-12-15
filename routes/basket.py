from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from app_models import Basket, Product, User

basket_bp = Blueprint('basket', __name__)

# Sepeti Görüntüleme
@basket_bp.route('', methods=['GET'])
@jwt_required()
def get_basket():
    current_user = get_jwt_identity()
    user = User.query.get(int(current_user))  # Kullanıcı bilgilerini al
    if not user:
        return jsonify({"error": "User not found"}), 404

    target_user_id = request.args.get("user_id", None)  # Admin için başka bir kullanıcı ID'si sağlanabilir

    # Admin başkalarının sepetine erişebilir
    if user.role == "admin" and target_user_id:
        basket_items = Basket.query.filter_by(user_id=int(target_user_id)).all()
    else:
        # Diğer kullanıcılar yalnızca kendi sepetini görebilir
        basket_items = Basket.query.filter_by(user_id=user.id).all()

    basket_products = []
    for item in basket_items:
        product = Product.query.get(item.product_id)
        if product:
            basket_products.append({
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity
            })

    return jsonify(basket_products), 200


# Sepete Ürün Ekleme
@basket_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_basket():
    current_user = get_jwt_identity()
    user = User.query.get(int(current_user))  # Kullanıcı bilgilerini al
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Sadece `user` veya `admin` rolündeki kullanıcılar sepete ürün ekleyebilir
    if user.role not in ["user", "admin"]:
        return jsonify({"error": "Unauthorized action. Only customers or admins can add to basket"}), 403

    data = request.json
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    # Ürünü kontrol et
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Sepette aynı ürün varsa miktarı güncelle
    existing_item = Basket.query.filter_by(user_id=user.id, product_id=product_id).first()
    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = Basket(user_id=user.id, product_id=product_id, quantity=quantity)
        db.session.add(new_item)

    db.session.commit()
    return jsonify({
        "product_id": product_id,
        "user_id": user.id,
        "message": "Product added to basket successfully"
    }), 201



# Sepetten Ürün Silme
@basket_bp.route('/delete/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_basket(product_id):
    current_user = get_jwt_identity()
    user = User.query.get(int(current_user))  # Kullanıcı bilgilerini al
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Sadece `user` rolündeki kullanıcılar sepetteki ürünü silebilir
    if user.role != "user":
        return jsonify({"error": "Unauthorized action. Only customers can remove from basket"}), 403

    # Sepetteki ürünü kontrol et
    item = Basket.query.filter_by(user_id=user.id, product_id=product_id).first()

    if not item:
        return jsonify({"error": "Product not found in basket"}), 404

    # Sepetten ürünü sil
    db.session.delete(item)
    db.session.commit()
    return jsonify({"product_id": product_id,"message": "Product removed from basket"}), 200  # product kendisi mesajda gözüksün

