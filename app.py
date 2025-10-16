from views.login_window import LoginWindow
from views.dashboard_window import DashboardWindow
class AppController:
    def __init__(self):
        self.user = None
        self.login_window = LoginWindow(self)
        self.dashboard = None
    def show_login(self):
        self.login_window.show()
    def login_success(self, user):
        self.user = user
        self.dashboard = DashboardWindow(self, user)
        try:
            self.login_window.close()
        except Exception:
            pass
        self.dashboard.show()
    def logout(self):
        try:
            if self.dashboard: self.dashboard.close()
        except Exception:
            pass
        self.user = None
        self.login_window = LoginWindow(self)
        self.login_window.show()
