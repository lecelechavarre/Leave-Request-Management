from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy, QLineEdit, QComboBox, QDateEdit, QCheckBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QDate
import os, datetime
from controllers.leave_controller import LeaveController
from views.leave_form import LeaveForm
from utils import load_prefs, save_prefs

def icon_path(name):
    return os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', name)

class DashboardWindow(QWidget):
    COLUMNS = ['ID', 'Username', 'Type', 'Start Date', 'End Date', 'Status', 'Reason']

    def __init__(self, app_controller, user):
        super().__init__()
        self.app_controller = app_controller
        self.user = user
        self.prefs = load_prefs() or {}
        self.setWindowTitle(f'Dashboard - {user["username"]} ({user.get("role")})')
        self.setFixedSize(980, 620)
        self.setup_ui()
        self.load_prefs()
        self.load_leaves()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        header_layout = QHBoxLayout()

        title = QLabel(f'Welcome, {self.user["username"]}')
        title.setProperty('heading', True)
        header_layout.addWidget(title)

        header_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        header_layout.addItem(header_spacer)

        self.refresh_btn = QPushButton('Refresh')
        self.refresh_btn.setIcon(QIcon(icon_path('refresh.svg')))
        self.refresh_btn.clicked.connect(self.load_leaves)
        header_layout.addWidget(self.refresh_btn)

        self.logout_btn = QPushButton('Logout')
        self.logout_btn.setIcon(QIcon(icon_path('logout.svg')))
        self.logout_btn.clicked.connect(self.on_logout)
        header_layout.addWidget(self.logout_btn)

        self.layout.addLayout(header_layout)

        # Search / filters / sort row
        controls_layout = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search by username, type, reason, status...')
        self.search.textChanged.connect(self.on_filters_changed)
        controls_layout.addWidget(self.search)

        self.status_filter = QComboBox()
        self.status_filter.addItems(['All', 'Pending', 'Approved', 'Rejected'])
        self.status_filter.currentIndexChanged.connect(self.on_filters_changed)
        controls_layout.addWidget(self.status_filter)

        self.type_filter = QComboBox()
        self.type_filter.addItems(['All', 'Vacation', 'Sick', 'Others'])
        self.type_filter.currentIndexChanged.connect(self.on_filters_changed)
        controls_layout.addWidget(self.type_filter)

        # Date range
        self.use_date_filter = QCheckBox('Use date range')
        self.use_date_filter.stateChanged.connect(self.on_filters_changed)
        controls_layout.addWidget(self.use_date_filter)

        self.start_filter = QDateEdit()
        self.start_filter.setCalendarPopup(True)
        self.start_filter.setDate(QDate.currentDate().addMonths(-1))
        self.start_filter.dateChanged.connect(self.on_filters_changed)
        controls_layout.addWidget(self.start_filter)

        self.end_filter = QDateEdit()
        self.end_filter.setCalendarPopup(True)
        self.end_filter.setDate(QDate.currentDate())
        self.end_filter.dateChanged.connect(self.on_filters_changed)
        controls_layout.addWidget(self.end_filter)

        self.sort_by = QComboBox()
        self.sort_by.addItems(['Start date ↑', 'Start date ↓', 'End date ↑', 'End date ↓', 'Username A-Z', 'Username Z-A', 'Status A-Z', 'Status Z-A'])
        self.sort_by.currentIndexChanged.connect(self.on_filters_changed)
        controls_layout.addWidget(self.sort_by)

        self.layout.addLayout(controls_layout)

        # Table
        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.layout.addWidget(self.table)

        # Actions
        action_layout = QHBoxLayout()
        self.add_btn = QPushButton('Apply Leave')
        self.add_btn.setIcon(QIcon(icon_path('add.svg')))
        self.add_btn.clicked.connect(self.open_add)
        action_layout.addWidget(self.add_btn)

        action_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.edit_btn = QPushButton('Edit')
        self.edit_btn.setIcon(QIcon(icon_path('edit.svg')))
        self.edit_btn.clicked.connect(self.edit_selected)
        action_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton('Delete')
        self.delete_btn.setIcon(QIcon(icon_path('delete.svg')))
        self.delete_btn.clicked.connect(self.delete_selected)
        action_layout.addWidget(self.delete_btn)

        self.approve_btn = QPushButton('Approve')
        self.approve_btn.setIcon(QIcon(icon_path('approve.svg')))
        self.approve_btn.clicked.connect(self.approve_selected)
        action_layout.addWidget(self.approve_btn)

        self.layout.addLayout(action_layout)
        self.setLayout(self.layout)

    def load_prefs(self):
        # load stored prefs for this user and apply to controls
        user_prefs = self.prefs.get(self.user['username'], {})
        if not user_prefs:
            return
        self.search.setText(user_prefs.get('search',''))
        self.status_filter.setCurrentText(user_prefs.get('status','All'))
        self.type_filter.setCurrentText(user_prefs.get('type','All'))
        self.sort_by.setCurrentText(user_prefs.get('sort','Start date ↑'))
        use_date = user_prefs.get('use_date', False)
        self.use_date_filter.setChecked(use_date)
        sd = user_prefs.get('start_date')
        ed = user_prefs.get('end_date')
        try:
            if sd:
                self.start_filter.setDate(QDate.fromString(sd, 'yyyy-MM-dd'))
            if ed:
                self.end_filter.setDate(QDate.fromString(ed, 'yyyy-MM-dd'))
        except Exception:
            pass

    def save_prefs(self):
        # save current control values for this user
        self.prefs[self.user['username']] = {
            'search': self.search.text().strip(),
            'status': self.status_filter.currentText(),
            'type': self.type_filter.currentText(),
            'sort': self.sort_by.currentText(),
            'use_date': bool(self.use_date_filter.isChecked()),
            'start_date': self.start_filter.date().toString('yyyy-MM-dd'),
            'end_date': self.end_filter.date().toString('yyyy-MM-dd')
        }
        save_prefs = getattr(__import__('utils'), 'save_prefs')
        save_prefs(self.prefs)

    def parse_date(self, s):
        try:
            return datetime.datetime.strptime(s, '%Y-%m-%d').date()
        except Exception:
            return None

    def on_filters_changed(self):
        # Save prefs and reload table live
        try:
            self.save_prefs()
        except Exception:
            pass
        self.load_leaves()

    def load_leaves(self):
        self.table.setRowCount(0)
        leaves = LeaveController.list(self.user)

        q = self.search.text().strip().lower()
        if q:
            leaves = [l for l in leaves if q in (l.get('username','').lower() + ' ' + l.get('type','').lower() + ' ' + l.get('reason','').lower() + ' ' + (l.get('status') or '').lower() + ' ' + l.get('start_date','') + ' ' + l.get('end_date',''))]

        # status filter
        status = self.status_filter.currentText()
        if status != 'All':
            leaves = [l for l in leaves if (l.get('status') or '').lower() == status.lower()]

        # type filter
        t = self.type_filter.currentText()
        if t != 'All':
            if t == 'Others':
                leaves = [l for l in leaves if l.get('type','').lower() not in ('vacation','sick')]
            else:
                leaves = [l for l in leaves if l.get('type','').lower() == t.lower()]

        # date range filter
        if self.use_date_filter.isChecked():
            sd = self.start_filter.date().toString('yyyy-MM-dd')
            ed = self.end_filter.date().toString('yyyy-MM-dd')
            try:
                sd_obj = datetime.datetime.strptime(sd, '%Y-%m-%d').date()
                ed_obj = datetime.datetime.strptime(ed, '%Y-%m-%d').date()
                leaves = [l for l in leaves if (l.get('start_date') and datetime.datetime.strptime(l.get('start_date'), '%Y-%m-%d').date() >= sd_obj and l.get('end_date') and datetime.datetime.strptime(l.get('end_date'), '%Y-%m-%d').date() <= ed_obj)]
            except Exception:
                pass

        # sorting (we'll let QTableWidget do column sorting, but pre-sort for default order)
        sort = self.sort_by.currentText()
        reverse = False
        keyfunc = None
        if sort == 'Start date ↑':
            keyfunc = lambda x: x.get('start_date') or ''
            reverse = False
        elif sort == 'Start date ↓':
            keyfunc = lambda x: x.get('start_date') or ''
            reverse = True
        elif sort == 'End date ↑':
            keyfunc = lambda x: x.get('end_date') or ''
            reverse = False
        elif sort == 'End date ↓':
            keyfunc = lambda x: x.get('end_date') or ''
            reverse = True
        elif sort == 'Username A-Z':
            keyfunc = lambda x: (x.get('username') or '').lower()
            reverse = False
        elif sort == 'Username Z-A':
            keyfunc = lambda x: (x.get('username') or '').lower()
            reverse = True
        elif sort == 'Status A-Z':
            keyfunc = lambda x: (x.get('status') or '').lower()
            reverse = False
        elif sort == 'Status Z-A':
            keyfunc = lambda x: (x.get('status') or '').lower()
            reverse = True

        if keyfunc:
            try:
                leaves = sorted(leaves, key=keyfunc, reverse=reverse)
            except Exception:
                pass

        # populate table
        for l in leaves:
            row = self.table.rowCount()
            self.table.insertRow(row)
            vals = [
                l.get('id',''),
                l.get('username',''),
                l.get('type',''),
                l.get('start_date',''),
                l.get('end_date',''),
                l.get('status',''),
                l.get('reason','')
            ]
            for col, v in enumerate(vals):
                item = QTableWidgetItem(v if v is not None else '')
                # align date columns center
                if col in (3,4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter.value)
                self.table.setItem(row, col, item)

        # allow clicking header to sort (Qt handles it), preserve default sort (we pre-sorted already)
        self.table.resizeColumnsToContents()

    def get_selected_id(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.warning(self, 'Warning', 'Select an item first')
            return None
        row = sel[0].row()
        item = self.table.item(row, 0)
        return item.text() if item else None

    def open_add(self):
        dlg = LeaveForm(self)
        if dlg.exec():
            payload = dlg.get_data()
            LeaveController.create(self.user, payload)
            self.load_leaves()

    def edit_selected(self):
        rid = self.get_selected_id()
        if not rid:
            return
        dlg = LeaveForm(self, leave_id=rid)
        if dlg.exec():
            payload = dlg.get_data()
            LeaveController.update(self.user, rid, payload)
            self.load_leaves()

    def delete_selected(self):
        rid = self.get_selected_id()
        if not rid:
            return
        LeaveController.delete(self.user, rid)
        self.load_leaves()

    def approve_selected(self):
        rid = self.get_selected_id()
        if not rid:
            return
        if self.user.get('role') != 'admin':
            QMessageBox.warning(self, 'Permission', 'Only admin can approve')
            return
        LeaveController.update(self.user, rid, {'status': 'Approved'})
        self.load_leaves()

    def on_logout(self):
        # save prefs and logout
        try:
            self.save_prefs()
        except Exception:
            pass
        self.app_controller.logout()
