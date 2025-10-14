from models.user_model import UserModel
from views.login_window import LoginWindow
from views.dashboard_window import DashboardWindow

class AppController:
    def __init__(self):
        self.user = None
        self.user_model = UserModel()
        self.login_window = LoginWindow(self)
        self.dashboard = None

    def show_login(self):
        self.login_window.show()

    def login_success(self, user):
        self.user = user
        self.dashboard = DashboardWindow(self, user)
        self.login_window.close()
        self.dashboard.show()

    def logout(self):
        if self.dashboard:
            self.dashboard.close()
        self.user = None
        # create a fresh login window
        self.login_window = LoginWindow(self)
        self.login_window.show()
