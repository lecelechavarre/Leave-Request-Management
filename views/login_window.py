from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QIcon
import os
from controllers.auth_controller import AuthController
from views.register_window import RegisterWindow

def icon_path(name):
    return os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', name)

class LoginWindow(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.setWindowTitle('Leave Manager - Login')
        self.setFixedSize(380, 250)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel('Leave Request Manager')
        title.setProperty('heading', True)
        layout.addWidget(title)

        layout.addWidget(QLabel('Username'))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel('Password'))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton('Login')
        self.login_btn.setIcon(QIcon(icon_path('user.svg')))
        self.login_btn.clicked.connect(self.on_login)
        btn_layout.addWidget(self.login_btn)

        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        btn_layout.addItem(spacer)

        self.register_btn = QPushButton('Create Account')
        self.register_btn.setProperty('class', 'secondary')
        self.register_btn.clicked.connect(self.on_register)
        btn_layout.addWidget(self.register_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def on_login(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        user = AuthController.login(u, p)
        if user:
            self.app_controller.login_success(user)
        else:
            QMessageBox.critical(self, 'Error', 'Invalid credentials')

    def on_register(self):
        reg = RegisterWindow(self)
        reg.exec()
