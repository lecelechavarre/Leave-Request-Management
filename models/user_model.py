import json, os, hashlib

class UserModel:
    def __init__(self, user_file="data/users.json"):
        self.user_file = user_file
        if not os.path.exists(self.user_file):
            with open(self.user_file, "w") as f:
                json.dump([], f)

    def load_users(self):
        with open(self.user_file, "r") as f:
            return json.load(f)

    def save_users(self, users):
        with open(self.user_file, "w") as f:
            json.dump(users, f, indent=2)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_user(self, username, password):
        users = self.load_users()
        for u in users:
            if u["username"] == username and u["password"] == self.hash_password(password):
                return u
        return None

    def username_exists(self, username):
        return any(u["username"] == username for u in self.load_users())

    def add_user(self, username, password, role):
        if self.username_exists(username):
            return False, "Username already exists."
        users = self.load_users()
        users.append({
            "username": username,
            "password": self.hash_password(password),
            "role": role
        })
        self.save_users(users)
        return True, "Account created successfully."
