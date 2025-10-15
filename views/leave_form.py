from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDateEdit, QTextEdit, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QDate
import os
from models.leave_model import LeaveModel

def icon_path(name):
    return os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', name)

class LeaveForm(QDialog):
    def __init__(self, parent=None, leave_id=None):
        super().__init__(parent)
        self.leave_id = leave_id
        self.setWindowTitle('Leave Form')
        self.setFixedSize(420, 380)
        self.setup_ui()
        if leave_id:
            self.load_existing()

    def setup_ui(self):
        layout = QVBoxLayout()
        title = QLabel('Leave request')
        title.setProperty('heading', True)
        layout.addWidget(title)

        layout.addWidget(QLabel('Type (Vacation / Sick)'))
        self.type_edit = QLineEdit()
        layout.addWidget(self.type_edit)

        row = QHBoxLayout()
        row.addWidget(QLabel('Start Date'))
        self.start = QDateEdit()
        self.start.setCalendarPopup(True)
        self.start.setDate(QDate.currentDate())
        row.addWidget(self.start)
        row.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        row.addWidget(QLabel('End Date'))
        self.end = QDateEdit()
        self.end.setCalendarPopup(True)
        self.end.setDate(QDate.currentDate())
        row.addWidget(self.end)
        layout.addLayout(row)

        layout.addWidget(QLabel('Reason'))
        self.reason = QTextEdit()
        self.reason.setFixedHeight(120)
        layout.addWidget(self.reason)

        btn_layout = QHBoxLayout()
        btn_layout.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.save_btn = QPushButton('Save')
        self.save_btn.setIcon(QIcon(icon_path('add.svg')))
        self.save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)
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
