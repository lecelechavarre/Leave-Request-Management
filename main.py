from PyQt6.QtWidgets import QApplication
from app import AppController
import sys, os
if __name__ == '__main__':
    app = QApplication(sys.argv)
    qss = os.path.join(os.path.dirname(__file__), 'resources', 'styles.qss')
    if os.path.exists(qss):
        with open(qss, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    c = AppController(); c.show_login(); sys.exit(app.exec())
