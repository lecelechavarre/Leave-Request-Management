from PyQt6.QtWidgets import QApplication, QMessageBox
from app import AppController
import sys, os
from logger import logger, exception_hook
sys.excepthook = exception_hook
if __name__ == '__main__':
    from models.init_db import init as init_db
    init_db()
    app = QApplication(sys.argv)
    controller = AppController(); controller.show_login()
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.exception('Application crashed: %s', e)
        QMessageBox.critical(None, 'Fatal', f'Application crashed: {e}')
