from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
from controllers import auth_controller as AC
from views.register_window import RegisterWindow
class LoginWindow(QWidget):
    def __init__(self, app_controller):
        super().__init__(); self.app_controller = app_controller; self.setWindowTitle('Login'); self.setFixedSize(420,260); self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout(); title = QLabel('Leave Request Manager'); title.setProperty('heading', True); layout.addWidget(title)
        layout.addWidget(QLabel('Username')); self.username = QLineEdit(); layout.addWidget(self.username)
        layout.addWidget(QLabel('Password')); self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.EchoMode.Password); layout.addWidget(self.password)
        btn = QHBoxLayout(); self.login_btn = QPushButton('Login'); self.login_btn.clicked.connect(self.on_login); btn.addWidget(self.login_btn); btn.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)); self.register_btn = QPushButton('Create Account'); self.register_btn.clicked.connect(self.on_register); btn.addWidget(self.register_btn); layout.addLayout(btn); self.setLayout(layout)
    def on_login(self):
        u = self.username.text().strip(); p = self.password.text().strip(); user = AC.login(u,p)
        if user: self.app_controller.login_success(user)
        else: QMessageBox.critical(self,'Error','Invalid credentials')
    def on_register(self): reg = RegisterWindow(self); reg.exec()
