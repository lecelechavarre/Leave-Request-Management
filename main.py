from PyQt6.QtWidgets import QApplication
from app import AppController
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = AppController()
    controller.show_login()
    sys.exit(app.exec())
