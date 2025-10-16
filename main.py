from PyQt6.QtWidgets import QApplication, QMessageBox
from app import AppController
import sys, os
from logger import logger, exception_hook
sys.excepthook = exception_hook
if __name__ == '__main__':
    app = QApplication(sys.argv)
    qss = os.path.join(os.path.dirname(__file__), 'resources', 'styles.qss')
    if os.path.exists(qss):
        with open(qss, 'r', encoding='utf-8') as f: app.setStyleSheet(f.read())
    controller = AppController(); controller.show_login()
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.exception('Application crashed: %s', e)
        QMessageBox.critical(None, 'Fatal', f'Application crashed: {e}')
