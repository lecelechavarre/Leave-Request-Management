from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox

class RegisterWindow(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Create Account")
        self.setGeometry(550, 350, 300, 250)

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm = QLineEdit()
        self.confirm.setPlaceholderText("Confirm Password")
        self.confirm.setEchoMode(QLineEdit.EchoMode.Password)

        self.role = QComboBox()
        self.role.addItems(["employee", "admin"])

        self.submit_btn = QPushButton("Register")
        self.submit_btn.clicked.connect(self.create_account)

        layout.addWidget(QLabel("<h3>Create Account</h3>"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.confirm)
        layout.addWidget(self.role)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

    def create_account(self):
        uname = self.username.text().strip()
        pwd = self.password.text().strip()
        confirm = self.confirm.text().strip()
        role = self.role.currentText()

        if not uname or not pwd or not confirm:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return
        if pwd != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        success, msg = self.controller.user_model.add_user(uname, pwd, role)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.close()
        else:
            QMessageBox.warning(self, "Error", msg)
