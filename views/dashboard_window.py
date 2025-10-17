from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableView, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy, QLineEdit, QComboBox, QToolBar, QInputDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from views.leave_table_model import LeaveTableModel
from views.leave_proxy import LeaveFilterProxy
from views.leave_form import LeaveForm
from views.csv_import_threaded import CSVImportDialog
from views.report_widget import ReportWidget
from controllers import leave_controller as LC
from utils import load_prefs, save_prefs
from logger import logger
import os
class DashboardWindow(QWidget):
    def __init__(self, app_controller, user):
        super().__init__(); self.app_controller = app_controller; self.user = user
        self.setWindowTitle(f'Dashboard - {user["username"]} ({user.get("role")})'); self.resize(1100,760)
        self.setup_ui(); self.load_prefs(); self.build_model(); self.load_leaves()
    def setup_ui(self):
        self.layout = QVBoxLayout(); toolbar = QToolBar(); self.theme_action = QAction('Toggle Theme'); self.theme_action.triggered.connect(self.toggle_theme); toolbar.addAction(self.theme_action); self.layout.addWidget(toolbar)
        header = QHBoxLayout(); title = QLabel(f'Welcome, {self.user["username"]}'); title.setProperty('heading', True); header.addWidget(title); header.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        self.refresh_btn = QPushButton('Refresh'); self.refresh_btn.clicked.connect(self.load_leaves); header.addWidget(self.refresh_btn)
        self.logout_btn = QPushButton('Logout'); self.logout_btn.clicked.connect(self.on_logout); header.addWidget(self.logout_btn)
        self.layout.addLayout(header)
        controls = QHBoxLayout(); self.search = QLineEdit(); self.search.setPlaceholderText('Search...'); self.search.textChanged.connect(self.on_filters_changed); controls.addWidget(self.search)
        self.status_filter = QComboBox(); self.status_filter.addItems(['All','Pending','Approved','Rejected']); self.status_filter.currentIndexChanged.connect(self.on_filters_changed); controls.addWidget(self.status_filter)
        self.type_filter = QComboBox(); self.type_filter.addItems(['All','Vacation','Sick','Others']); self.type_filter.currentIndexChanged.connect(self.on_filters_changed); controls.addWidget(self.type_filter)
        self.import_btn = QPushButton('Import CSV'); self.import_btn.clicked.connect(self.open_import); controls.addWidget(self.import_btn)
        self.layout.addLayout(controls)
        self.summary = QLabel(''); self.layout.addWidget(self.summary)
        self.view = QTableView(); self.layout.addWidget(self.view)
        actions = QHBoxLayout(); self.add_btn = QPushButton('Apply Leave'); self.add_btn.clicked.connect(self.open_add); actions.addWidget(self.add_btn); actions.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)); self.edit_btn = QPushButton('Edit'); self.edit_btn.clicked.connect(self.edit_selected); actions.addWidget(self.edit_btn); self.approve_btn = QPushButton('Approve'); self.approve_btn.clicked.connect(self.approve_selected); actions.addWidget(self.approve_btn); self.delete_btn = QPushButton('Delete'); self.delete_btn.clicked.connect(self.delete_selected); actions.addWidget(self.delete_btn); self.layout.addLayout(actions)
        self.report = ReportWidget(self.user); self.layout.addWidget(self.report); self.setLayout(self.layout)
    def build_model(self):
        self.model = LeaveTableModel(user=self.user)
        self.proxy = LeaveFilterProxy(self); self.proxy.setSourceModel(self.model); self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.view.setModel(self.proxy); self.view.setSortingEnabled(True)
    def load_prefs(self):
        p = load_prefs(); up = p.get(self.user['username'], {}); self.search.setText(up.get('search','')); self.status_filter.setCurrentText(up.get('status','All')); self.type_filter.setCurrentText(up.get('type','All')); theme = p.get('theme','light'); self.apply_theme(theme)
    def save_prefs(self):
        p = load_prefs(); p[self.user['username']] = {'search': self.search.text(), 'status': self.status_filter.currentText(), 'type': self.type_filter.currentText()}; save_prefs(p)
    def on_filters_changed(self):
        self.save_prefs(); self.apply_filters()
    def apply_filters(self):
        self.proxy.set_filters(search=self.search.text(), status=self.status_filter.currentText(), type_=self.type_filter.currentText(), use_date=False)
    def load_leaves(self):
        try:
            self.model.refresh_all()
            all_leaves = LC.list_for(self.user); total = len(LC.list_for(self.user)); approved = len([l for l in all_leaves if (l.get('status') or '').lower() == 'approved']); pending = len([l for l in all_leaves if (l.get('status') or '').lower() == 'pending']); rejected = len([l for l in all_leaves if (l.get('status') or '').lower() == 'rejected'])
            self.summary.setText(f"Total Requests: {total} | Approved: {approved} | Pending: {pending} | Rejected: {rejected}"); self.apply_filters(); self.report.draw_chart()
        except Exception as e:
            logger.exception('load_leaves failed: %s', e)
    def get_selected_record(self):
        sel = self.view.selectionModel().selectedRows(); 
        if not sel: return None
        proxy_idx = sel[0]; src_idx = self.proxy.mapToSource(proxy_idx); row = src_idx.row(); return self.model._rows[row]
    def edit_selected(self):
        data = self.get_selected_record(); 
        if not data: QMessageBox.warning(self,'Select','Select a leave'); return
        dlg = LeaveForm(self, leave_id=data.get('id'), user=self.user)
        if dlg.exec(): from controllers.leave_controller import update; update(self.user, data.get('id'), dlg.get_data()); self.load_leaves()
    def open_add(self):
        dlg = LeaveForm(self, user=self.user)
        if dlg.exec(): from controllers.leave_controller import create; create(self.user, dlg.get_data()); self.load_leaves()
    def delete_selected(self):
        data = self.get_selected_record(); 
        if not data: QMessageBox.warning(self,'Select','Select a leave'); return
        from controllers.leave_controller import delete; delete(self.user, data.get('id')); self.load_leaves()
    def approve_selected(self):
        data = self.get_selected_record(); 
        if not data: QMessageBox.warning(self,'Select','Select a leave'); return
        if self.user.get('role') not in ('admin','manager'): QMessageBox.warning(self,'Permission','Only admin/manager can approve'); return
        remarks, ok = QInputDialog.getText(self, 'Approve', 'Remarks (optional):')
        if ok:
            from controllers.leave_controller import approve; approve(self.user, data.get('id'), remarks or ''); self.load_leaves()
    def open_import(self):
        dlg = CSVImportDialog(self, user=self.user); 
        if dlg.exec(): self.load_leaves()
    def toggle_theme(self):
        p = load_prefs(); cur = p.get('theme','light'); nxt = 'dark' if cur=='light' else 'light'; p['theme']=nxt; save_prefs(p); self.apply_theme(nxt)
    def apply_theme(self, theme):
        if theme == 'dark':
            qss = """QWidget{background:#1e1e1e;color:#ddd}QLineEdit,QTextEdit{background:#2b2b2b;color:#fff}QPushButton{background:#3a7bd5;color:#fff;border-radius:6px}"""
        else:
            qss = """QWidget{background:#f7f9fc;color:#222}QLineEdit,QTextEdit{background:#fff;color:#000}QPushButton{background:#2f7fe6;color:#fff;border-radius:6px}"""
        self.setStyleSheet(qss); self.report.draw_chart()
    def on_logout(self): self.save_prefs(); self.app_controller.logout()
