from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from app_models import Product, Purchase ,User

products_bp = Blueprint('products', __name__)

#Ürün ekleme
@products_bp.route('/add', methods=['POST'])
@jwt_required()
def add_product():
    current_user = get_jwt_identity()

    # Kullanıcının rolünü kontrol et
    user = User.query.get(int(current_user))
    if not user or user.role not in ["admin", "seller"]:
        return jsonify({"error": "You do not have permission to add products"}), 403

    data = request.get_json()

    # Veri doğrulama
    required_fields = ["name", "brand", "category", "price", "stock"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    try:
        # Yeni ürün oluştur
        new_product = Product(
            name=data.get("name"),
            brand=data.get("brand"),
            category=data.get("category"),
            price=float(data.get("price")),  # Fiyatın float olduğundan emin olun
            stock=int(data.get("stock")),  # Stok miktarının integer olduğundan emin olun
            seller_id=current_user,  # Giriş yapan kullanıcının ID'si
            image_url=data.get("image_url"),
            description=data.get("description"),
            is_active=data.get("is_active", True),
            is_featured=data.get("is_featured", False),
            discounted_price=float(data.get("discounted_price")) if data.get("discounted_price") else None
        )
        db.session.add(new_product)
        db.session.commit()

        return jsonify({"message": "Product added successfully!", "id": new_product.id}), 201

    except ValueError as e:
        return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred while adding the product"}), 500



#Ürün listeleme
@products_bp.route('/list', methods=['GET'])
def list_products():
    try:
        # Sayfa ve sayfa başına ürün sayısını al
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Minimum ve maksimum sınırlar (isteğe bağlı)
        if page < 1 or per_page < 1 or per_page > 100:
            return jsonify({"error": "Invalid page or per_page value"}), 400

        # Ürünleri al ve sayfaya göre ayır
        products = Product.query.paginate(page=page, per_page=per_page, error_out=False)

        # Ürünleri JSON formatında döndür
        return jsonify({
            "products": [{
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "price": p.price,
                "discounted_price": p.discounted_price,
                "image_url": p.image_url,
                "description": p.description,
                "stock": p.stock,
                "is_featured": p.is_featured
            } for p in products.items],
            "total": products.total,
            "pages": products.pages,
            "current_page": products.page
        }), 200
    except Exception as e:
        # Genel bir hata mesajı döndür
        return jsonify({"error": "An error occurred while listing products"}), 500


# 2. Ürün Detayları
@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "price": product.price,
        "discounted_price": product.discounted_price,
        "image_url": product.image_url,
        "description": product.description,
        "stock": product.stock,
        "is_featured": product.is_featured
    }), 200

# 3. Ürün Satın Alma
@products_bp.route('/buy/<int:product_id>', methods=['POST'])
@jwt_required()
def buy_product(product_id):
    data = request.json
    current_user = get_jwt_identity()

    # Kullanıcı verisini kontrol et
    user = User.query.get(int(current_user))
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Yalnızca "user" ve "admin" rolleri satın alma yapabilir
    if user.role not in ["user", "admin"]:
        return jsonify({"error": "Only users and admins can make purchases"}), 403

    quantity = data.get("quantity", 1)
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Stok kontrolü
    if product.stock < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    # Satın alma işlemi
    purchase = Purchase(
        user_id=user.id,
        product_id=product_id,
        quantity=quantity
    )
    product.stock -= quantity
    db.session.add(purchase)
    db.session.commit()

    return jsonify({
        "message": "Purchase successful!",
        "product_id": product_id,
        "remaining_stock": product.stock
    }), 200


# 4. Ürün Silme
@products_bp.route('/delete/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    current_user = get_jwt_identity()  # Kullanıcı kimliği doğrulaması yapılır

    # Kullanıcı bilgilerini kontrol et
    user = User.query.get(int(current_user))
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Ürünü al
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Yalnızca admin veya ürünün sahibi olan satıcı ürünü silebilir
    if user.role == "admin" or product.seller_id == user.id:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully!"}), 200
    else:
        return jsonify({"error": "Unauthorized action"}), 403

