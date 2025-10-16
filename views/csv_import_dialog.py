from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QMessageBox
from controllers.leave_controller import create
import csv, datetime
class CSVImportDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle('Import CSV - preview')
        self.setFixedSize(600,400)
        layout = QVBoxLayout()
        layout.addWidget(QLabel('CSV preview (first 100 lines):'))
        self.preview = QTextEdit(); self.preview.setReadOnly(True); layout.addWidget(self.preview)
        btn_layout = QVBoxLayout()
        self.load_btn = QPushButton('Choose CSV'); self.load_btn.clicked.connect(self.load_csv); layout.addWidget(self.load_btn)
        self.import_btn = QPushButton('Import into DB'); self.import_btn.clicked.connect(self.do_import); layout.addWidget(self.import_btn)
        self.setLayout(layout)
        self.rows = []
    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV (*.csv)')
        if not path: return
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.rows = []
                txt = []
                for i, r in enumerate(reader):
                    if i >= 100:
                        break
                    self.rows.append(r)
                    txt.append(str(r))
                self.preview.setPlainText('\n'.join(txt))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to read CSV: {e}')
    def do_import(self):
        if not self.rows:
            QMessageBox.warning(self, 'No data', 'No CSV loaded')
            return
        count = 0
        for r in self.rows:
            # expected columns: type,start_date,end_date,reason (username taken from logged-in user)
            payload = {
                'type': r.get('type') or r.get('Type') or '',
                'start_date': r.get('start_date') or r.get('Start Date') or datetime.date.today().isoformat(),
                'end_date': r.get('end_date') or r.get('End Date') or datetime.date.today().isoformat(),
                'reason': r.get('reason') or r.get('Reason') or ''
            }
            create(self.user, payload); count += 1
        QMessageBox.information(self, 'Imported', f'Imported {count} rows (previewed only first 100).')
        self.accept()
