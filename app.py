from views.login_window import LoginWindow
from models.user_model import UserModel

class AppController:
    def __init__(self):
        self.user_model = UserModel()
        self.login_window = None

    def show_login(self):
        self.login_window = LoginWindow(self)
        self.login_window.show()

    def login_success(self, user):
        print(f"Login success: {user['username']} ({user['role']})")
