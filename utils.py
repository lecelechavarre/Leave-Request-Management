import json, os, hashlib, secrets, binascii

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)
    elif isinstance(salt, str):
        salt = binascii.unhexlify(salt)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return binascii.hexlify(salt).decode() + '$' + binascii.hexlify(dk).decode()

def verify_password(password, stored):
    try:
        salt_hex, dk_hex = stored.split('$')
        salt = binascii.unhexlify(salt_hex)
        check = hash_password(password, salt)
        return check == stored
    except Exception:
        return False
