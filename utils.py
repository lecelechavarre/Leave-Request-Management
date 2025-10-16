import json, os
PREFS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'preferences.json')
from passlib.hash import bcrypt
def hash_password(pw): return bcrypt.hash(pw)
def verify_password(pw, hashed): 
    try:
        return bcrypt.verify(pw, hashed)
    except Exception:
        return False
def load_prefs():
    try:
        if not os.path.exists(PREFS_PATH): return {}
        with open(PREFS_PATH, 'r', encoding='utf-8') as f: return json.load(f)
    except Exception:
        return {}
def save_prefs(p):
    os.makedirs(os.path.dirname(PREFS_PATH), exist_ok=True)
    with open(PREFS_PATH, 'w', encoding='utf-8') as f: json.dump(p, f, indent=2)
