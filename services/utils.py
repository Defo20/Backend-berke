from werkzeug.security import generate_password_hash, check_password_hash

# Şifreyi hashleme
def hash_password(password):
    return generate_password_hash(password, method='pbkdf2:sha256')

# Şifre doğrulama
def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)
