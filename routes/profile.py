from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from app_models import User, Product, Purchase
from services.utils import verify_password, hash_password 

profile_bp = Blueprint('profile', __name__)

# Kullanıcı Login işlemi
@profile_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    # Kullanıcı doğrulama işlemi (email ve şifre kontrolü)
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not verify_password(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    # JWT Token oluşturma (kimlik doğrulamada hem ID hem rol ekleniyor)
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})  

    return jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "role": user.role
    }), 200



# Kullanıcı Kayıt işlemi (Signup)
@profile_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()  # JSON verisini al
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    phone = data.get("phone")
    role = data.get("role", "user")  # Varsayılan rol "user" olarak atanır

    # Kullanıcı zaten var mı kontrol et
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"error": "Kullanıcı zaten mevcut"}), 400

    # Yeni kullanıcı oluştur
    hashed_password = hash_password(password)  # Şifreyi hashle
    new_user = User(email=email, password=hashed_password, name=name, phone=phone, role=role)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!", "user_id": new_user.id, "role": new_user.role}), 201


# Kullanıcı Profili Bilgilerini Getir
@profile_bp.route('', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()  # Token'den kimliği al
    user = User.query.get(current_user)  # Eğer kimlik sadece ID ise, doğrudan kullan

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Kullanıcının rolüne göre dönecek veriyi özelleştirme
    profile_data = {
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "photo": user.profile_photo if user.profile_photo else "default-profile-photo.jpg",
        "role": user.role, # Kullanıcının rolünü de döndürüyoruz
        "user_id":user.id
    }
    # Eğer admin ise ek bilgiler dönebiliriz
    if user.role == "admin":
        profile_data["permissions"] = ["add_user", "delete_user", "manage_products"]

    # Eğer seller ise farklı bilgiler dönebilir
    elif user.role == "seller":
        profile_data["permissions"] = ["add_product", "update_product", "view_sales"]
    # Eğer normal bir kullanıcı ise (user), minimum bilgi döndürebiliriz
    elif user.role == "user":
        profile_data["permissions"] = ["view_products", "purchase_products"]

    return jsonify(profile_data), 200



# Kullanıcı Profili Bilgilerini Güncelle
@profile_bp.route('/update', methods=['POST'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()  # Token'dan kimliği al
    user = User.query.get(int(current_user))  # Veritabanından mevcut kullanıcıyı getir
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json  # Gelen JSON verisi

    # Admin işlemleri
    if user.role == "admin":
        target_user_id = data.get("user_id")
        if target_user_id:  # Eğer admin başka bir kullanıcıyı güncelliyorsa
            target_user = User.query.get(target_user_id)
            if not target_user:
                return jsonify({"error": "Target user not found"}), 404

            # Diğer kullanıcının bilgilerini güncelle
            target_user.name = data.get("name", target_user.name)
            target_user.email = data.get("email", target_user.email)
            target_user.phone = data.get("phone", target_user.phone)
            target_user.profile_photo = data.get("photo", target_user.profile_photo)
            db.session.commit()
            return jsonify({"message": f"User {target_user_id} profile updated successfully by admin"}), 200
        else:
            return jsonify({"error": "No target user ID provided"}), 400

    # Kullanıcı kendi profilini güncelleyebilir
    elif user.role in ["user", "seller"]:
        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)
        user.phone = data.get("phone", user.phone)
        user.profile_photo = data.get("photo", user.profile_photo)
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200

    # Yetkisiz erişim
    return jsonify({"error": "Unauthorized action"}), 403





# Kullanıcının Satın Aldığı Ürünleri Getir
@profile_bp.route('/purchased-products', methods=['GET'])
@jwt_required()
def get_purchased_products():
    current_user = get_jwt_identity()

    # Kullanıcının veritabanındaki kaydını al
    user = User.query.get(int(current_user))
    if not user:
        return jsonify({"error": "User not found"}), 404

    purchased_products = []

    if user.role == "admin":
        # Admin, tüm kullanıcıların satın alımlarını görebilir
        purchases = Purchase.query.all()
    elif user.role == "seller":
        # Seller, sadece kendi ürünlerine ait satın alımları görebilir
        purchases = Purchase.query.join(Product).filter(Product.seller_id == user.id).all()
    else:  # "user" rolü
        # User, sadece kendi satın alımlarını görebilir
        purchases = Purchase.query.filter_by(user_id=user.id).all()
        
    if not purchases:
        # Eğer herhangi bir satın alma kaydı yoksa
        return jsonify({"message": "No purchases found for this user"}), 200

    for purchase in purchases:
        product = Product.query.get(purchase.product_id)  # Ürünü veritabanından al
        if product:
            purchased_products.append({
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "discountPrice": product.discounted_price,
                "photo": product.image_url,
                "quantity": purchase.quantity,  # Satın alınan miktar
                "purchase_date": purchase.purchase_date.strftime('%Y-%m-%d %H:%M:%S')  # Tarih formatı
            })

    return jsonify(purchased_products), 200

