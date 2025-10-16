import os, json, hashlib, secrets, binascii
PREFS_PATH = os.path.join(os.path.dirname(__file__),'data','preferences.json')
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)
    elif isinstance(salt, str):
        salt = binascii.unhexlify(salt)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(salt).decode() + '$' + binascii.hexlify(dk).decode()

def verify_password(password, stored):
    try:
        salt_hex, dk_hex = stored.split('$')
        salt = binascii.unhexlify(salt_hex)
        check = hash_password(password, salt)
        return check == stored
    except Exception:
        return False

def load_prefs():
    try:
        if not os.path.exists(PREFS_PATH):
            return {}
        with open(PREFS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_prefs(p):
    os.makedirs(os.path.dirname(PREFS_PATH), exist_ok=True)
    with open(PREFS_PATH, 'w', encoding='utf-8') as f:
        json.dump(p, f, indent=2)
