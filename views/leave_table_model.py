from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from models.db_alchemy import SessionLocal
from models.models_alchemy import Leave
PAGE = 100
class LeaveTableModel(QAbstractTableModel):
    HEADERS = ['ID','Username','Type','Start Date','End Date','Status','Approved By','Approved Date','Remarks']
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self._rows = []
        self.loaded = 0
        self.total = self._count_total()
        self.fetchMore(QModelIndex())
    def _count_total(self):
        db = SessionLocal()
        try:
            q = db.query(Leave)
            if self.user and self.user.get('role') != 'admin':
                q = q.filter(Leave.username==self.user.get('username'))
            return q.count()
        finally:
            db.close()
    def canFetchMore(self, parent):
        return self.loaded < self.total
    def fetchMore(self, parent):
        db = SessionLocal()
        try:
            q = db.query(Leave)
            if self.user and self.user.get('role') != 'admin':
                q = q.filter(Leave.username==self.user.get('username'))
            rows = q.offset(self.loaded).limit(PAGE).all()
            count = len(rows)
            if count == 0: return
            self.beginInsertRows(QModelIndex(), self.loaded, self.loaded + count - 1)
            for r in rows:
                d = {k: getattr(r,k) for k in ['id','username','type','start_date','end_date','status','approved_by','approved_date','remarks']}
                self._rows.append(d)
            self.loaded += count
            self.endInsertRows()
        finally:
            db.close()
    def rowCount(self, parent=QModelIndex()):
        return len(self._rows)
    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid(): return None
        r = self._rows[index.row()]; col = index.column()
        keys = ['id','username','type','start_date','end_date','status','approved_by','approved_date','remarks']
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole): return r.get(keys[col], '') or ''
        if role == Qt.ItemDataRole.UserRole: return r
        return None
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole: return self.HEADERS[section]
        return None
    def flags(self, index):
        if not index.isValid(): return Qt.ItemFlag.ItemIsEnabled
        col = index.column(); flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if col in (2,5):
            if self.user and self.user.get('role') != 'admin' and col == 5:
                return flags
            return flags | Qt.ItemFlag.ItemIsEditable
        return flags
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid(): return False
        row = index.row(); col = index.column(); keymap = ['id','username','type','start_date','end_date','status','approved_by','approved_date','remarks']; key = keymap[col]
        self._rows[row][key] = str(value)
        from controllers.leave_controller import update
        update(self.user, self._rows[row]['id'], {key: self._rows[row][key]})
        self.dataChanged.emit(index, index, [role]); return True
    def refresh_all(self):
        self.beginResetModel(); self._rows = []; self.loaded = 0; self.total = self._count_total(); self.fetchMore(QModelIndex()); self.endResetModel()
