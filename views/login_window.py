from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from views.register_window import RegisterWindow

class LoginWindow(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.controller = app_controller
        self.setWindowTitle("Login - Leave Manager")
        self.setGeometry(500, 300, 300, 200)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("Login")
        self.create_btn = QPushButton("Create Account")

        layout.addWidget(QLabel("<h3>Leave Request Manager</h3>"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.create_btn)

        self.setLayout(layout)

        self.login_btn.clicked.connect(self.handle_login)
        self.create_btn.clicked.connect(self.open_register)

    def handle_login(self):
        uname = self.username.text().strip()
        pwd = self.password.text().strip()
        if not uname or not pwd:
            QMessageBox.warning(self, "Error", "Please enter username and password.")
            return

        user = self.controller.user_model.verify_user(uname, pwd)
        if user:
            self.controller.login_success(user)
            self.close()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid credentials.")

    def open_register(self):
        reg = RegisterWindow(self.controller)
        reg.exec()
