from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QIcon
import os
from controllers.auth_controller import AuthController

def icon_path(name):
    return os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', name)

class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Create Account')
        self.setFixedSize(360, 320)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        title = QLabel('Create account')
        title.setProperty('heading', True)
        layout.addWidget(title)

        layout.addWidget(QLabel('Username'))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel('Password'))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        layout.addWidget(QLabel('Confirm Password'))
        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm)

        layout.addWidget(QLabel('Role'))
        self.role = QComboBox()
        self.role.addItems(['employee', 'admin'])
        layout.addWidget(self.role)

        btn_layout = QHBoxLayout()
        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        btn_layout.addItem(spacer)
        self.register_btn = QPushButton('Register')
        self.register_btn.setIcon(QIcon(icon_path('add.svg')))
        self.register_btn.clicked.connect(self.register_user)
        btn_layout.addWidget(self.register_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def register_user(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        c = self.confirm.text().strip()
        r = self.role.currentText()
        if not u or not p:
            QMessageBox.warning(self, 'Error', 'All fields are required')
            return
        if p != c:
            QMessageBox.warning(self, 'Error', 'Passwords do not match')
            return
        success = AuthController.register(u, p, r)
        if success:
            QMessageBox.information(self, 'Success', 'Account created successfully!')
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Username already exists')
