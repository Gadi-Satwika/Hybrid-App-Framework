import sys
import requests
import webbrowser  # New import for opening the PDF in the browser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                             QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QInputDialog, QLineEdit

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#ffffff')
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        user, ok1 = QInputDialog.getText(self, "Login", "Username:")
        password, ok2 = QInputDialog.getText(self, "Login", "Password:", QLineEdit.Password)

        if not ok1 or not ok2:
            sys.exit() # Close app if they cancel login

        self.auth = (user, password) # Store credentials dynamically
        
        # Test connection
        try:
            res = requests.get('http://127.0.0.1:8000/api/upload/', auth=self.auth)
            if res.status_code != 200:
                QMessageBox.critical(self, "Error", "Invalid Login")
                sys.exit()
        except:
            QMessageBox.critical(self, "Error", "Server Offline")
            sys.exit()

        self.setWindowTitle("Industrial Equipment Analyzer Pro")
        self.setGeometry(100, 100, 1000, 850) # Slightly wider for more buttons
        self.auth = ('admin', 'Satwika@1916')
        
        self.setStyleSheet("""
            QMainWindow { background-color: #f8fafc; }
            QPushButton { background-color: #2563eb; color: white; border-radius: 4px; padding: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #1d4ed8; }
            #Header { font-size: 24px; font-weight: bold; color: #1e3a8a; }
            #StatBox { background-color: #eff6ff; border-left: 5px solid #3b82f6; padding: 15px; }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("Equipment Analytics Dashboard")
        header.setObjectName("Header")
        main_layout.addWidget(header)

        self.upload_btn = QPushButton("Import CSV Dataset")
        self.upload_btn.setFixedSize(200, 40)
        self.upload_btn.clicked.connect(self.upload_file)
        main_layout.addWidget(self.upload_btn)

        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("StatBox")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel("Ready for data import.")
        stats_layout.addWidget(self.stats_label)
        self.stats_frame.setLayout(stats_layout)
        main_layout.addWidget(self.stats_frame)

        self.canvas = MplCanvas(self)
        main_layout.addWidget(self.canvas)

        main_layout.addWidget(QLabel("<b>Server History Management</b>"))
        self.history_table = QTableWidget(0, 4) # 4 columns now
        self.history_table.setHorizontalHeaderLabels(["File Name", "Date", "Analysis", "Management"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setFixedHeight(200)
        main_layout.addWidget(self.history_table)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.fetch_history()

    def fetch_history(self):
        try:
            response = requests.get('http://127.0.0.1:8000/api/upload/', auth=self.auth)
            if response.status_code == 200:
                self.populate_table(response.json())
        except Exception as e:
            print(f"Sync Error: {e}")

    def populate_table(self, data):
        self.history_table.setRowCount(0)
        for row, item in enumerate(data):
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(item['file_name']))
            self.history_table.setItem(row, 1, QTableWidgetItem(item['date']))
            
            # Column 2: View Button
            view_btn = QPushButton("View")
            view_btn.setStyleSheet("background-color: #10b981;")
            view_btn.clicked.connect(lambda ch, d=item['summary']: self.update_ui(d))
            self.history_table.setCellWidget(row, 2, view_btn)

            # Column 3: PDF and Delete (Using a layout inside the cell)
            manage_widget = QWidget()
            manage_layout = QHBoxLayout(manage_widget)
            manage_layout.setContentsMargins(2, 2, 2, 2)
            
            pdf_btn = QPushButton("PDF")
            pdf_btn.setStyleSheet("background-color: #f59e0b;")
            pdf_btn.clicked.connect(lambda ch, i=item['id']: self.download_pdf(i))
            
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("background-color: #ef4444;")
            del_btn.clicked.connect(lambda ch, i=item['id']: self.delete_record(i))
            
            manage_layout.addWidget(pdf_btn)
            manage_layout.addWidget(del_btn)
            self.history_table.setCellWidget(row, 3, manage_widget)

    def download_pdf(self, report_id):
        # We trigger the PDF generation URL in the default browser
        url = f"http://127.0.0.1:8000/api/report/{report_id}/"
        webbrowser.open(url)

    def delete_record(self, report_id):
        reply = QMessageBox.question(self, 'Confirm Delete', 'Are you sure you want to delete this record?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                response = requests.delete(f"http://127.0.0.1:8000/api/delete/{report_id}/", auth=self.auth)
                if response.status_code == 204:
                    self.fetch_history()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete: {e}")

    def upload_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'rb') as f:
                res = requests.post('http://127.0.0.1:8000/api/upload/', files={'file': f}, auth=self.auth)
                if res.status_code == 200:
                    self.update_ui(res.json())
                    self.fetch_history()

    def update_ui(self, data):
        stats = (f"<b>ANALYSIS</b><br>Total: {data['total_count']} | "
                 f"Temp: {data['avg_temp']:.2f}°C | Press: {data['avg_pressure']:.2f} bar")
        self.stats_label.setText(stats)
        self.canvas.axes.cla()
        self.canvas.axes.bar(list(data['type_distribution'].keys()), list(data['type_distribution'].values()), color='#3b82f6')
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())