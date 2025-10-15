from PyQt6.QtWidgets import QApplication
from app import AppController
import sys, os

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # load QSS
    qss_path = os.path.join(os.path.dirname(__file__), 'resources', 'styles.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    controller = AppController()
    controller.show_login()
    sys.exit(app.exec())
