from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDateEdit, QTextEdit, QMessageBox
from PyQt6.QtCore import QDate
from models.leave_model import LeaveModel

class LeaveForm(QDialog):
    def __init__(self, parent=None, leave_id=None):
        super().__init__(parent)
        self.leave_id = leave_id
        self.setWindowTitle('Leave Form')
        self.setup_ui()
        if leave_id:
            self.load_existing()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Type (Vacation/Sick)'))
        self.type_edit = QLineEdit()
        layout.addWidget(self.type_edit)
        layout.addWidget(QLabel('Start Date'))
        self.start = QDateEdit()
        self.start.setCalendarPopup(True)
        self.start.setDate(QDate.currentDate())
        layout.addWidget(self.start)
        layout.addWidget(QLabel('End Date'))
        self.end = QDateEdit()
        self.end.setCalendarPopup(True)
        self.end.setDate(QDate.currentDate())
        layout.addWidget(self.end)
        layout.addWidget(QLabel('Reason'))
        self.reason = QTextEdit()
        layout.addWidget(self.reason)
        btn = QPushButton('Save')
        btn.clicked.connect(self.on_save)
        layout.addWidget(btn)
        self.setLayout(layout)

    def load_existing(self):
        leaves = LeaveModel.list_for_user(None)
        for l in leaves:
            if l['id'] == self.leave_id:
                self.type_edit.setText(l.get('type', ''))
                self.start.setDate(QDate.fromString(l.get('start_date'), 'yyyy-MM-dd'))
                self.end.setDate(QDate.fromString(l.get('end_date'), 'yyyy-MM-dd'))
                self.reason.setPlainText(l.get('reason', ''))

    def on_save(self):
        # basic validation
        t = self.type_edit.text().strip()
        sd = self.start.date()
        ed = self.end.date()
        if not t:
            QMessageBox.warning(self, 'Error', 'Type is required')
            return
        if ed < sd:
            QMessageBox.warning(self, 'Error', 'End date must be after start date')
            return
        self.accept()

    def get_data(self):
        return {
            'type': self.type_edit.text().strip(),
            'start_date': self.start.date().toString('yyyy-MM-dd'),
            'end_date': self.end.date().toString('yyyy-MM-dd'),
            'reason': self.reason.toPlainText().strip()
        }
