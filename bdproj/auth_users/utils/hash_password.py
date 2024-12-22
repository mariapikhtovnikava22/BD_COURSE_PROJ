import hashlib

def hash_password(password):
    """Хэширует пароль."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password, hashed_password):
    """Проверяет, совпадает ли пароль с хэшем."""
    return hash_password(password) == hashed_password