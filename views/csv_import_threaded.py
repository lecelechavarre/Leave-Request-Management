from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
import csv, datetime
from controllers.leave_controller import create
class ImportThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(int)
    def __init__(self, rows, user):
        super().__init__(); self.rows = rows; self.user = user
    def run(self):
        count = 0
        for i, r in enumerate(self.rows):
            payload = {
                'type': r.get('type') or r.get('Type') or '',
                'start_date': r.get('start_date') or r.get('Start Date') or datetime.date.today().isoformat(),
                'end_date': r.get('end_date') or r.get('End Date') or datetime.date.today().isoformat(),
                'reason': r.get('reason') or r.get('Reason') or ''
            }
            create(self.user, payload); count += 1
            if i % 5 == 0: self.progress.emit(i)
        self.finished.emit(count)
class CSVImportDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent); self.user = user; self.setWindowTitle('Import CSV - threaded'); self.setFixedSize(640,420); self.setup_ui(); self.rows=[]
    def setup_ui(self):
        layout = QVBoxLayout(); layout.addWidget(QLabel('CSV preview (first 200 lines):')); self.preview = QTextEdit(); self.preview.setReadOnly(True); layout.addWidget(self.preview)
        self.load_btn = QPushButton('Choose CSV'); self.load_btn.clicked.connect(self.load_csv); layout.addWidget(self.load_btn)
        self.import_btn = QPushButton('Import into DB (threaded)'); self.import_btn.clicked.connect(self.do_import); layout.addWidget(self.import_btn)
        self.setLayout(layout)
    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV (*.csv)')
        if not path: return
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.rows = []
                txt = []
                for i, r in enumerate(reader):
                    if i >= 200: break
                    self.rows.append(r); txt.append(str(r))
                self.preview.setPlainText('\n'.join(txt))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to read CSV: {e}')
    def do_import(self):
        if not self.rows:
            QMessageBox.warning(self, 'No data', 'No CSV loaded'); return
        self.thread = ImportThread(self.rows, self.user)
        self.thread.progress.connect(lambda i: self.preview.append(f'Imported {i} rows...'))
        self.thread.finished.connect(self._on_import_finished)
        self.thread.start()
    def _on_import_finished(self, c):
        try:
            QMessageBox.information(self, 'Imported', f'Imported {c} rows.')
            self.accept()
        except Exception:
            pass
