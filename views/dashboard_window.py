from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTreeView, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy, QLineEdit, QComboBox, QDateEdit, QCheckBox, QToolButton, QFileDialog, QTableView
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QDate
from views.leave_table_model import LeaveTableModel
from views.leave_proxy import LeaveFilterProxy
from views.leave_form import LeaveForm
from views.csv_import_dialog import CSVImportDialog
from controllers import leave_controller as LC
from utils import load_prefs, save_prefs
from logger import logger
import datetime, csv, os
def icon_path(n): return os.path.join(os.path.dirname(__file__),'..','resources','icons',n)
class DashboardWindow(QWidget):
    def __init__(self, app_controller, user):
        super().__init__()
        self.app_controller = app_controller; self.user = user
        self.setWindowTitle(f'Dashboard - {user["username"]} ({user.get("role")})'); self.setFixedSize(1100,700)
        self.setup_ui(); self.load_prefs(); self.build_model(); self.load_leaves()
    def setup_ui(self):
        self.layout = QVBoxLayout(); header = QHBoxLayout()
        title = QLabel(f'Welcome, {self.user["username"]}'); title.setProperty('heading', True); header.addWidget(title)
        header.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        self.refresh_btn = QPushButton('Refresh'); self.refresh_btn.clicked.connect(self.load_leaves); header.addWidget(self.refresh_btn)
        self.logout_btn = QPushButton('Logout'); self.logout_btn.clicked.connect(self.on_logout); header.addWidget(self.logout_btn)
        self.layout.addLayout(header)
        controls = QHBoxLayout(); self.search = QLineEdit(); self.search.setPlaceholderText('Search...'); self.search.textChanged.connect(self.on_filters_changed); controls.addWidget(self.search)
        self.status_filter = QComboBox(); self.status_filter.addItems(['All','Pending','Approved','Rejected']); self.status_filter.currentIndexChanged.connect(self.on_filters_changed); controls.addWidget(self.status_filter)
        self.type_filter = QComboBox(); self.type_filter.addItems(['All','Vacation','Sick','Others']); self.type_filter.currentIndexChanged.connect(self.on_filters_changed); controls.addWidget(self.type_filter)
        self.use_date = QCheckBox('Use date range'); self.use_date.stateChanged.connect(self.on_filters_changed); controls.addWidget(self.use_date)
        self.start_date = QDateEdit(); self.start_date.setCalendarPopup(True); self.start_date.setDate(QDate.currentDate().addMonths(-1)); self.start_date.dateChanged.connect(self.on_filters_changed); controls.addWidget(self.start_date)
        self.end_date = QDateEdit(); self.end_date.setCalendarPopup(True); self.end_date.setDate(QDate.currentDate()); self.end_date.dateChanged.connect(self.on_filters_changed); controls.addWidget(self.end_date)
        self.import_btn = QPushButton('Import CSV'); self.import_btn.clicked.connect(self.open_import); controls.addWidget(self.import_btn)
        self.layout.addLayout(controls)
        self.summary = QLabel(''); self.layout.addWidget(self.summary)
        self.view = QTableView(); self.view.setSelectionBehavior(self.view.SelectionBehavior.SelectRows); self.layout.addWidget(self.view)
        actions = QHBoxLayout(); self.add_btn = QPushButton('Apply Leave'); self.add_btn.clicked.connect(self.open_add); actions.addWidget(self.add_btn)
        actions.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        self.edit_btn = QPushButton('Edit'); self.edit_btn.clicked.connect(self.edit_selected); actions.addWidget(self.edit_btn)
        self.delete_btn = QPushButton('Delete'); self.delete_btn.clicked.connect(self.delete_selected); actions.addWidget(self.delete_btn)
        self.approve_btn = QPushButton('Approve'); self.approve_btn.clicked.connect(self.approve_selected); actions.addWidget(self.approve_btn)
        self.layout.addLayout(actions); self.setLayout(self.layout)
    def build_model(self):
        self.model = LeaveTableModel(user=self.user)
        self.proxy = LeaveFilterProxy(self)
        self.proxy.setSourceModel(self.model)
        self.view.setModel(self.proxy)
        # enable sorting
        self.view.setSortingEnabled(True)
    def load_prefs(self):
        try:
            p = load_prefs(); up = p.get(self.user['username'], {})
            self.search.setText(up.get('search','')); self.status_filter.setCurrentText(up.get('status','All')); self.type_filter.setCurrentText(up.get('type','All'))
            self.use_date.setChecked(up.get('use_date', False))
        except Exception:
            pass
    def save_prefs(self):
        try:
            p = load_prefs(); p[self.user['username']] = {'search': self.search.text(), 'status': self.status_filter.currentText(), 'type': self.type_filter.currentText(), 'use_date': bool(self.use_date.isChecked())}; save_prefs(p)
        except Exception as e:
            logger.exception('save_prefs failed: %s', e)
    def on_filters_changed(self):
        self.save_prefs(); self.apply_filters()
    def apply_filters(self):
        sd = self.start_date.date().toString('yyyy-MM-dd') if self.use_date.isChecked() else None
        ed = self.end_date.date().toString('yyyy-MM-dd') if self.use_date.isChecked() else None
        self.proxy.set_filters(search=self.search.text(), status=self.status_filter.currentText(), type_=self.type_filter.currentText(), use_date=self.use_date.isChecked(), start_date=sd, end_date=ed)
    def load_leaves(self):
        try:
            self.model.refresh()
            all_leaves = LC.list_for(self.user); total = len(all_leaves)
            approved = len([l for l in all_leaves if (l.get('status') or '').lower() == 'approved'])
            pending = len([l for l in all_leaves if (l.get('status') or '').lower() == 'pending'])
            rejected = len([l for l in all_leaves if (l.get('status') or '').lower() == 'rejected'])
            self.summary.setText(f"Total Requests: {total} | Approved: {approved} | Pending: {pending} | Rejected: {rejected}")
            self.apply_filters()
        except Exception as e:
            logger.exception('load_leaves failed: %s', e)
    def get_selected_record(self):
        sel = self.view.selectionModel().selectedRows()
        if not sel: return None
        proxy_idx = sel[0]
        src_idx = self.proxy.mapToSource(proxy_idx)
        row = src_idx.row()
        return self.model._rows[row]
    def edit_selected(self):
        data = self.get_selected_record()
        if not data: QMessageBox.warning(self,'Select','Select a leave'); return
        dlg = LeaveForm(self, leave_id=data.get('id'))
        if dlg.exec(): LC.update(self.user, data.get('id'), dlg.get_data()); self.load_leaves()
    def open_add(self):
        dlg = LeaveForm(self)
        if dlg.exec(): LC.create(self.user, dlg.get_data()); self.load_leaves()
    def delete_selected(self):
        data = self.get_selected_record()
        if not data: QMessageBox.warning(self,'Select','Select a leave'); return
        LC.delete(self.user, data.get('id')); self.load_leaves()
    def approve_selected(self):
        data = self.get_selected_record()
        if not data: QMessageBox.warning(self,'Select','Select a leave'); return
        if self.user.get('role') != 'admin': QMessageBox.warning(self,'Permission','Only admin can approve'); return
        LC.update(self.user, data.get('id'), {'status':'Approved'}); self.load_leaves()
    def copy_selected(self):
        data = self.get_selected_record()
        if not data: QMessageBox.information(self,'Copy','No row selected'); return
        import pyperclip
        pyperclip.copy(','.join([str(data.get(k,'')) for k in ['id','username','type','start_date','end_date','status','reason']]))
        QMessageBox.information(self,'Copied','Copied row to clipboard')
    def open_import(self):
        dlg = CSVImportDialog(self, user=self.user)
        if dlg.exec(): self.load_leaves()
    def on_logout(self): self.save_prefs(); self.app_controller.logout()
