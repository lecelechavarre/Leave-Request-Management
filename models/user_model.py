from utils import load_json, save_json, hash_password, verify_password
import os

USERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')

class UserModel:
    @classmethod
    def _ensure_file(cls):
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
            default = [
                { "username": "admin", "password": hash_password("admin"), "role": "admin" },
                { "username": "employee", "password": hash_password("employee"), "role": "employee" }
            ]
            save_json(USERS_FILE, default)

    @classmethod
    def load_all(cls):
        cls._ensure_file()
        return load_json(USERS_FILE)

    @classmethod
    def get_user(cls, username):
        for u in cls.load_all():
            if u['username'] == username:
                return u
        return None

    @classmethod
    def verify(cls, username, password):
        u = cls.get_user(username)
        if not u:
            return False
        return verify_password(password, u['password'])

    @classmethod
    def username_exists(cls, username):
        return cls.get_user(username) is not None

    @classmethod
    def add_user(cls, username, password, role='employee'):
        cls._ensure_file()
        if cls.username_exists(username):
            return False
        users = load_json(USERS_FILE)
        users.append({
            'username': username,
            'password': hash_password(password),
            'role': role
        })
        save_json(USERS_FILE, users)
        return True

    @classmethod
    def all_users(cls):
        return cls.load_all()
