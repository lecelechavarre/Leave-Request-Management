from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDateEdit, QTextEdit, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import QDate
from models import leave_model as LM
class LeaveForm(QDialog):
    def __init__(self,parent=None,leave_id=None):
        super().__init__(parent); self.leave_id=leave_id; self.setWindowTitle('Leave Form'); self.setFixedSize(460,420); self.setup_ui(); 
        if leave_id: self.load_existing()
    def setup_ui(self):
        layout=QVBoxLayout(); layout.addWidget(QLabel('Leave request')); layout.addWidget(QLabel('Type (Vacation / Sick / Others)')); self.type_edit=QLineEdit(); layout.addWidget(self.type_edit)
        row=QHBoxLayout(); row.addWidget(QLabel('Start Date')); self.start=QDateEdit(); self.start.setCalendarPopup(True); self.start.setDate(QDate.currentDate()); row.addWidget(self.start); row.addItem(QSpacerItem(10,10,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)); row.addWidget(QLabel('End Date')); self.end=QDateEdit(); self.end.setCalendarPopup(True); self.end.setDate(QDate.currentDate()); row.addWidget(self.end); layout.addLayout(row)
        layout.addWidget(QLabel('Reason')); self.reason=QTextEdit(); self.reason.setFixedHeight(160); layout.addWidget(self.reason)
        btn_layout=QHBoxLayout(); btn_layout.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)); self.save_btn=QPushButton('Save'); self.save_btn.clicked.connect(self.on_save); btn_layout.addWidget(self.save_btn); layout.addLayout(btn_layout); self.setLayout(layout)
    def load_existing(self):
        items=LM.list_all()
        for l in items:
            if l.get('id')==self.leave_id:
                self.type_edit.setText(l.get('type','')); self.start.setDate(QDate.fromString(l.get('start_date'),'yyyy-MM-dd')); self.end.setDate(QDate.fromString(l.get('end_date'),'yyyy-MM-dd')); self.reason.setPlainText(l.get('reason',''))
    def on_save(self):
        t=self.type_edit.text().strip(); sd=self.start.date(); ed=self.end.date()
        if not t: QMessageBox.warning(self,'Error','Type required'); return
        if ed < sd: QMessageBox.warning(self,'Error','End must be after start'); return
        self.accept()
    def get_data(self):
        return {'type': self.type_edit.text().strip(), 'start_date': self.start.date().toString('yyyy-MM-dd'), 'end_date': self.end.date().toString('yyyy-MM-dd'), 'reason': self.reason.toPlainText().strip()}
