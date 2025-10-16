from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant
from models.db_alchemy import SessionLocal
from models.models_alchemy import Leave
class LeaveTableModel(QAbstractItemModel):
    HEADERS = ['ID','Username','Type','Start Date','End Date','Status','Reason']
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self._rows = []
        self.load_rows()
    def load_rows(self):
        db = SessionLocal()
        try:
            if self.user and self.user.get('role') != 'admin':
                rows = db.query(Leave).filter(Leave.username==self.user.get('username')).all()
            else:
                rows = db.query(Leave).all()
            self._rows = [r.__dict__ for r in rows]
            # SQLAlchemy row contains _sa_instance_state remove it
            for r in self._rows:
                if '_sa_instance_state' in r: del r['_sa_instance_state']
        finally:
            db.close()
    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            # parent used for grouping not implemented here
            return 0
        return len(self._rows)
    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)
    def index(self, row, column, parent=QModelIndex()):
        if self.hasIndex(row, column, parent):
            return self.createIndex(row, column)
        return QModelIndex()
    def parent(self, index):
        return QModelIndex()
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid(): return None
        r = self._rows[index.row()]
        col = index.column()
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            mapping = ['id','username','type','start_date','end_date','status','reason']
            return r.get(mapping[col], '')
        if role == Qt.ItemDataRole.UserRole:
            return r
        return None
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.HEADERS[section]
        return None
    def flags(self, index):
        if not index.isValid(): return Qt.ItemFlag.NoItemFlags
        col = index.column()
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if col in (2,5):  # Type and Status editable
            if self.user and self.user.get('role') != 'admin' and col == 5:
                return flags
            return flags | Qt.ItemFlag.ItemIsEditable
        return flags
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid(): return False
        row = index.row(); col = index.column()
        keymap = ['id','username','type','start_date','end_date','status','reason']
        key = keymap[col]
        self._rows[row][key] = str(value)
        # persist to DB via controller to keep audit logic
        from controllers.leave_controller import update
        update(self.user, self._rows[row]['id'], {key: self._rows[row][key]})
        self.dataChanged.emit(index, index, [role])
        return True
    def refresh(self):
        self.beginResetModel(); self.load_rows(); self.endResetModel()
