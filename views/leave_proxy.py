from PyQt6.QtCore import QSortFilterProxyModel, Qt
import datetime
class LeaveFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search = ''
        self.status = 'All'
        self.type = 'All'
        self.use_date = False
        self.start_date = None
        self.end_date = None
    def set_filters(self, search='', status='All', type_='All', use_date=False, start_date=None, end_date=None):
        self.search = (search or '').lower().strip()
        self.status = status or 'All'
        self.type = type_ or 'All'
        self.use_date = bool(use_date)
        self.start_date = start_date
        self.end_date = end_date
        self.invalidateFilter()
    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        if model is None: return True
        def data(col):
            idx = model.index(source_row, col, source_parent)
            val = model.data(idx)
            return '' if val is None else str(val).lower()
        if self.search:
            text = ' '.join([data(c) for c in range(model.columnCount())])
            if self.search not in text: return False
        if self.status != 'All' and data(5) != self.status.lower(): return False
        if self.type != 'All':
            if self.type == 'Others' and data(2) in ('vacation','sick'): return False
            elif self.type != 'Others' and data(2) != self.type.lower(): return False
        if self.use_date and self.start_date and self.end_date:
            try:
                sd = datetime.datetime.strptime(self.start_date, '%Y-%m-%d').date()
                ed = datetime.datetime.strptime(self.end_date, '%Y-%m-%d').date()
                a = datetime.datetime.strptime(data(3), '%Y-%m-%d').date()
                b = datetime.datetime.strptime(data(4), '%Y-%m-%d').date()
                if a < sd or b > ed: return False
            except Exception:
                return False
        return True
