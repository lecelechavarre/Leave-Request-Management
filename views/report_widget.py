from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from controllers.leave_controller import list_for
class ReportWidget(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent); self.user = user; self.setup_ui(); self.draw_chart()
    def setup_ui(self):
        layout = QVBoxLayout(); layout.addWidget(QLabel('Reports')); self.canvas = FigureCanvas(Figure(figsize=(5,3))); layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.subplots(); self.refresh_btn = QPushButton('Refresh'); self.refresh_btn.clicked.connect(self.draw_chart); layout.addWidget(self.refresh_btn); self.setLayout(layout)
    def draw_chart(self):
        rows = list_for(self.user)
        counts = {}
        for r in rows:
            k = (r.get('status') or 'Unknown')
            counts[k] = counts.get(k, 0) + 1
        labels = list(counts.keys()); values = [counts[k] for k in labels]
        self.ax.clear(); self.ax.pie(values, labels=labels, autopct='%d'); self.ax.set_title('Requests by Status'); self.canvas.draw()
