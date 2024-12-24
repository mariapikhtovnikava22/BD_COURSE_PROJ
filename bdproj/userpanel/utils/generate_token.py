import uuid

def generate_token():
    """Генерирует уникальный токен."""
    return str(uuid.uuid4().hex)