from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout, QMessageBox
from controllers.leave_controller import LeaveController
from views.leave_form import LeaveForm

class DashboardWindow(QWidget):
    def __init__(self, app_controller, user):
        super().__init__()
        self.app_controller = app_controller
        self.user = user
        self.setWindowTitle(f'Dashboard - {user["username"]} ({user.get("role")})')
        self.setup_ui()
        self.load_leaves()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel(f'Welcome, {self.user["username"]}'))

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Apply Leave')
        self.add_btn.clicked.connect(self.open_add)
        btn_layout.addWidget(self.add_btn)
        self.refresh_btn = QPushButton('Refresh')
        self.refresh_btn.clicked.connect(self.load_leaves)
        btn_layout.addWidget(self.refresh_btn)
        self.logout_btn = QPushButton('Logout')
        self.logout_btn.clicked.connect(self.app_controller.logout)
        btn_layout.addWidget(self.logout_btn)
        self.layout.addLayout(btn_layout)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        action_layout = QHBoxLayout()
        self.edit_btn = QPushButton('Edit')
        self.edit_btn.clicked.connect(self.edit_selected)
        action_layout.addWidget(self.edit_btn)
        self.delete_btn = QPushButton('Delete')
        self.delete_btn.clicked.connect(self.delete_selected)
        action_layout.addWidget(self.delete_btn)
        self.approve_btn = QPushButton('Approve')
        self.approve_btn.clicked.connect(self.approve_selected)
        action_layout.addWidget(self.approve_btn)
        self.layout.addLayout(action_layout)

        self.setLayout(self.layout)

    def load_leaves(self):
        self.list_widget.clear()
        leaves = LeaveController.list(self.user)
        for l in leaves:
            text = f"{l['id']} | {l['username']} | {l['type']} | {l['start_date']} -> {l['end_date']} | {l.get('status')}"
            self.list_widget.addItem(text)

    def get_selected_id(self):
        it = self.list_widget.currentItem()
        if not it:
            QMessageBox.warning(self, 'Warning', 'Select an item first')
            return None
        return it.text().split('|')[0].strip()

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
