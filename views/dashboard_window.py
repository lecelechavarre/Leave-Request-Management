from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTreeView, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy, QLineEdit, QComboBox, QDateEdit, QCheckBox, QToolButton, QFileDialog
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import Qt, QDate
from controllers import leave_controller as LC
from views.leave_form import LeaveForm
from views.leave_proxy import LeaveFilterProxy
from utils import load_prefs, save_prefs
from logger import logger
import datetime, csv, os

def icon_path(n): return os.path.join(os.path.dirname(__file__),'..','resources','icons',n)

class DashboardWindow(QWidget):
    HEADERS = ['ID','Username','Type','Start Date','End Date','Status','Reason']

    def __init__(self, app_controller, user):
        super().__init__()
        self.app_controller = app_controller
        self.user = user
        self.prefs = load_prefs() or {}
        self.expanded_states = self.prefs.get('expanded', {})
        self.setWindowTitle(f'Dashboard - {user["username"]} ({user.get("role")})')
        self.setFixedSize(1100,700)
        self.setup_ui()
        self.load_prefs()
        self.build_model()
        self.load_leaves()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        header = QHBoxLayout()
        title = QLabel(f'Welcome, {self.user["username"]}'); title.setProperty('heading', True); header.addWidget(title)
        header.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        self.refresh_btn = QPushButton('Refresh'); self.refresh_btn.clicked.connect(self.load_leaves); header.addWidget(self.refresh_btn)
        self.logout_btn = QPushButton('Logout'); self.logout_btn.clicked.connect(self.on_logout); header.addWidget(self.logout_btn)
        self.layout.addLayout(header)

        controls = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText('Search...'); self.search.textChanged.connect(self.on_filters_changed); controls.addWidget(self.search)
        self.group_mode = QComboBox(); self.group_mode.addItems(['Group by Status','Group by Username','No Grouping']); self.group_mode.currentIndexChanged.connect(self.on_group_changed); controls.addWidget(self.group_mode)
        self.status_filter = QComboBox(); self.status_filter.addItems(['All','Pending','Approved','Rejected']); self.status_filter.currentIndexChanged.connect(self.on_filters_changed); controls.addWidget(self.status_filter)
        self.type_filter = QComboBox(); self.type_filter.addItems(['All','Vacation','Sick','Others']); self.type_filter.currentIndexChanged.connect(self.on_filters_changed); controls.addWidget(self.type_filter)
        self.use_date = QCheckBox('Use date range'); self.use_date.stateChanged.connect(self.on_filters_changed); controls.addWidget(self.use_date)
        self.start_date = QDateEdit(); self.start_date.setCalendarPopup(True); self.start_date.setDate(QDate.currentDate().addMonths(-1)); self.start_date.dateChanged.connect(self.on_filters_changed); controls.addWidget(self.start_date)
        self.end_date = QDateEdit(); self.end_date.setCalendarPopup(True); self.end_date.setDate(QDate.currentDate()); self.end_date.dateChanged.connect(self.on_filters_changed); controls.addWidget(self.end_date)
        self.copy_btn = QToolButton(); self.copy_btn.setToolTip('Copy selected rows'); self.copy_btn.clicked.connect(self.copy_selected); controls.addWidget(self.copy_btn)
        self.export_btn = QToolButton(); self.export_btn.setToolTip('Export ALL rows to CSV'); self.export_btn.clicked.connect(self.export_all); controls.addWidget(self.export_btn)
        self.layout.addLayout(controls)

        self.summary = QLabel(''); self.layout.addWidget(self.summary)

        self.view = QTreeView(); self.view.setRootIsDecorated(False); self.view.setAlternatingRowColors(True)
        self.view.setEditTriggers(QTreeView.EditTrigger.DoubleClicked | QTreeView.EditTrigger.SelectedClicked)
        self.view.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.view.expanded.connect(self.on_expanded); self.view.collapsed.connect(self.on_collapsed)
        self.layout.addWidget(self.view)

        actions = QHBoxLayout()
        self.add_btn = QPushButton('Apply Leave'); self.add_btn.clicked.connect(self.open_add); actions.addWidget(self.add_btn)
        actions.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        self.edit_btn = QPushButton('Edit'); self.edit_btn.clicked.connect(self.edit_selected); actions.addWidget(self.edit_btn)
        self.delete_btn = QPushButton('Delete'); self.delete_btn.clicked.connect(self.delete_selected); actions.addWidget(self.delete_btn)
        self.approve_btn = QPushButton('Approve'); self.approve_btn.clicked.connect(self.approve_selected); actions.addWidget(self.approve_btn)
        self.layout.addLayout(actions)
        self.setLayout(self.layout)

    def build_model(self):
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.HEADERS)
        self.proxy = LeaveFilterProxy(self)
        self.proxy.setSourceModel(self.model)
        # PyQt6 enum: Qt.CaseSensitivity.CaseInsensitive
        self.proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.view.setModel(self.proxy)
        try:
            self.model.itemChanged.connect(self.on_item_changed)
        except Exception as e:
            logger.exception('connecting itemChanged failed: %s', e)

    def load_prefs(self):
        userprefs = self.prefs.get(self.user['username'], {})
        if not userprefs: return
        self.search.setText(userprefs.get('search',''))
        self.status_filter.setCurrentText(userprefs.get('status','All'))
        self.type_filter.setCurrentText(userprefs.get('type','All'))
        self.group_mode.setCurrentText(userprefs.get('group','Group by Status'))
        self.use_date.setChecked(userprefs.get('use_date', False))
        sd = userprefs.get('start_date'); ed = userprefs.get('end_date')
        try:
            if sd: self.start_date.setDate(QDate.fromString(sd, 'yyyy-MM-dd'))
            if ed: self.end_date.setDate(QDate.fromString(ed, 'yyyy-MM-dd'))
        except Exception:
            pass

    def save_prefs(self):
        try:
            p = load_prefs()
            p[self.user['username']] = {
                'search': self.search.text().strip(),
                'status': self.status_filter.currentText(),
                'type': self.type_filter.currentText(),
                'group': self.group_mode.currentText(),
                'use_date': bool(self.use_date.isChecked()),
                'start_date': self.start_date.date().toString('yyyy-MM-dd'),
                'end_date': self.end_date.date().toString('yyyy-MM-dd'),
            }
            save_prefs(p)
        except Exception as e:
            logger.exception('save_prefs failed: %s', e)

    def on_group_changed(self):
        self.save_prefs(); self.build_model(); self.load_leaves()

    def on_filters_changed(self):
        self.save_prefs(); self.apply_proxy_filters()

    def apply_proxy_filters(self):
        try:
            sd = self.start_date.date().toString('yyyy-MM-dd') if self.use_date.isChecked() else None
            ed = self.end_date.date().toString('yyyy-MM-dd') if self.use_date.isChecked() else None
            self.proxy.set_filters(search=self.search.text(), status=self.status_filter.currentText(), type_=self.type_filter.currentText(), use_date=self.use_date.isChecked(), start_date=sd, end_date=ed)
        except Exception as e:
            logger.exception('apply_proxy_filters failed: %s', e)

    def get_all_leaves(self):
        return LC.list_for(self.user)

    def filtered_leaves(self):
        return self.get_all_leaves()

    def load_leaves(self):
        try:
            self.model.removeRows(0, self.model.rowCount())
            leaves = self.filtered_leaves()
            all_leaves = self.get_all_leaves()
            total = len(all_leaves)
            approved = len([l for l in all_leaves if (l.get('status') or '').lower() == 'approved'])
            pending = len([l for l in all_leaves if (l.get('status') or '').lower() == 'pending'])
            rejected = len([l for l in all_leaves if (l.get('status') or '').lower() == 'rejected'])
            self.summary.setText(f"Total Requests: {total} | Approved: {approved} | Pending: {pending} | Rejected: {rejected}")

            mode = self.group_mode.currentText()
            if mode == 'Group by Status':
                groups = {}
                for l in leaves: groups.setdefault(l.get('status') or 'Unknown', []).append(l)
                for gname, items in groups.items():
                    parent_items = [QStandardItem(gname)] + [QStandardItem('') for _ in range(len(self.HEADERS)-1)]
                    self.model.appendRow(parent_items)
                    for it in items:
                        child = self._create_row_item(it, editable=True)
                        parent_items[0].appendRow(child)
                    idx = self.model.indexFromItem(parent_items[0])
                    if self.expanded_states.get(self.user['username'], {}).get(gname, True):
                        self.view.expand(self.proxy.mapFromSource(idx))
            elif mode == 'Group by Username':
                groups = {}
                for l in leaves: groups.setdefault(l.get('username') or 'Unknown', []).append(l)
                for gname, items in groups.items():
                    parent_items = [QStandardItem(gname)] + [QStandardItem('') for _ in range(len(self.HEADERS)-1)]
                    self.model.appendRow(parent_items)
                    for it in items:
                        child = self._create_row_item(it, editable=True)
                        parent_items[0].appendRow(child)
                    idx = self.model.indexFromItem(parent_items[0])
                    if self.expanded_states.get(self.user['username'], {}).get(gname, True):
                        self.view.expand(self.proxy.mapFromSource(idx))
            else:
                for it in leaves:
                    row = self._create_row_item(it, editable=True)
                    self.model.appendRow(row)

            self.apply_proxy_filters()
            for c in range(self.model.columnCount()):
                try:
                    self.view.resizeColumnToContents(c)
                except Exception:
                    pass
        except Exception as e:
            logger.exception('load_leaves failed: %s', e)

    def _create_row_item(self, record, editable=False):
        cols = [
            record.get('id',''),
            record.get('username',''),
            record.get('type',''),
            record.get('start_date',''),
            record.get('end_date',''),
            record.get('status',''),
            record.get('reason','')
        ]
        items = []
        for i,v in enumerate(cols):
            si = QStandardItem(str(v))
            if editable and i in (2,5):
                if i == 5 and self.user.get('role') != 'admin':
                    si.setEditable(False)
                else:
                    si.setEditable(True)
            else:
                si.setEditable(False)
            if i == 6 and v:
                si.setToolTip(v)
            if i == 0:
                si.setData(record, Qt.ItemDataRole.UserRole)
            items.append(si)
        return items

    def get_selected_record(self):
        sel = self.view.selectionModel().selectedRows()
        if not sel: return None
        idx = sel[0]
        source_idx = self.proxy.mapToSource(idx)
        item = self.model.itemFromIndex(source_idx)
        data = item.data(Qt.ItemDataRole.UserRole)
        if data: return data
        row_id = item.text()
        for r in range(self.model.rowCount()):
            parent = self.model.item(r,0)
            for c in range(parent.rowCount() if parent.hasChildren() else 0):
                child = parent.child(c,0)
                if child and child.text() == row_id:
                    return child.data(Qt.ItemDataRole.UserRole)
        return None

    def edit_selected(self):
        data = self.get_selected_record()
        if not data: QMessageBox.warning(self,'Select','Select a leave (child row) to edit'); return
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

    def on_item_changed(self, item):
        try:
            data = item.data(Qt.ItemDataRole.UserRole)
            if not data: return
            col = item.column()
        except Exception:
            return
        rec = dict(data)
        if col == 2: rec['type'] = item.text()
        elif col == 5: rec['status'] = item.text()
        else: return
        LC.update(self.user, rec.get('id'), {'type': rec.get('type'), 'status': rec.get('status')})
        self.load_leaves()

    def copy_selected(self):
        sel = self.view.selectionModel().selectedRows()
        rows = []
        for idx in sel:
            source_idx = self.proxy.mapToSource(idx)
            item = self.model.itemFromIndex(source_idx)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data:
                rows.append([data.get('id',''), data.get('username',''), data.get('type',''), data.get('start_date',''), data.get('end_date',''), data.get('status',''), data.get('reason','')])
        if not rows: QMessageBox.information(self,'Copy','No rows selected'); return
        txt = '\n'.join([','.join(['"{}"'.format(str(x).replace('"','""')) for x in r]) for r in rows])
        clipboard = self.view.window().clipboard(); clipboard.setText(txt); QMessageBox.information(self,'Copied',f'Copied {len(rows)} rows to clipboard')

    def export_all(self):
        all_leaves = LC.list_for(self.user) if self.user.get('role') == 'admin' else LC.list_for(self.user)
        path, _ = QFileDialog.getSaveFileName(self, 'Export CSV', os.path.expanduser('~/leaves_export.csv'), 'CSV Files (*.csv)')
        if not path: return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f); writer.writerow(self.HEADERS)
                for l in all_leaves: writer.writerow([l.get('id',''), l.get('username',''), l.get('type',''), l.get('start_date',''), l.get('end_date',''), l.get('status',''), l.get('reason','')])
            QMessageBox.information(self,'Exported',f'Exported {len(all_leaves)} rows to {path}')
        except Exception as e: logger.exception('export_all failed: %s', e); QMessageBox.critical(self,'Error',f'Export failed: {e}')

    def on_expanded(self, index):
        try:
            source_idx = self.proxy.mapToSource(index)
            item = self.model.itemFromIndex(source_idx)
            if not item: return
            key = item.text(); user = self.user['username']; self.expanded_states.setdefault(user, {})[key] = True; self.prefs['expanded'] = self.expanded_states; save_prefs(self.prefs)
        except Exception as e:
            logger.exception('on_expanded failed: %s', e)

    def on_collapsed(self, index):
        try:
            source_idx = self.proxy.mapToSource(index)
            item = self.model.itemFromIndex(source_idx)
            if not item: return
            key = item.text(); user = self.user['username']; self.expanded_states.setdefault(user, {})[key] = False; self.prefs['expanded'] = self.expanded_states; save_prefs(self.prefs)
        except Exception as e:
            logger.exception('on_collapsed failed: %s', e)

    def on_logout(self):
        try:
            self.prefs['expanded'] = self.expanded_states; save_prefs(self.prefs)
        except Exception:
            pass
        self.app_controller.logout()
