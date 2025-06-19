from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QFrame, QSizePolicy, QStackedWidget, QTextEdit, QFileDialog, QComboBox, QDateEdit
)
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QDate
import sys
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from db_config import get_connection

class MembersPage(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Top area: title and search
        top_layout = QHBoxLayout()
        title = QLabel("Members Management")
        title.setStyleSheet("color: white; font-size: 30px;")
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search by name or ID")
        search_bar.setStyleSheet("padding: 8px; font-size: 14px; border: 2px solid #00FFFF; border-radius: 10px; color: white; background-color: #2E2E2E;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(search_bar)
        main_layout.addLayout(top_layout)

        # Button area
        button_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_add.clicked.connect(self.add_member)

        self.btn_update = QPushButton("Update")
        self.btn_update.clicked.connect(self.update_member)

        self.btn_delete = QPushButton("Delete")
        self.btn_clear = QPushButton("Clear")
        self.btn_export = QPushButton("Export")

        for btn in [self.btn_add, self.btn_update, self.btn_delete, self.btn_clear, self.btn_export]:
            btn.setStyleSheet("background-color: #00FFFF; color: black; font-weight: bold; padding: 10px; border-radius: 8px;")
            button_layout.addWidget(btn)

        # Content layout: form | image | table
        content_layout = QHBoxLayout()

        # --- Left: Form ---
        form_layout = QVBoxLayout()
        def create_input(label_text):
            label = QLabel(label_text)
            label.setStyleSheet("color: white;")
            input_field = QLineEdit()
            input_field.setStyleSheet("background-color: #2E2E2E; color: white; padding: 10px; border-radius: 10px;")
            return label, input_field

        fields = ["Member ID", "Name", "Status", "Address", "Phone Number", "Email", "Membership Plan", "Start Date", "Total Billed"]
        self.inputs = {}
        for field in fields:
            label, widget = create_input(field)
            form_layout.addWidget(label)
            form_layout.addWidget(widget)
            self.inputs[field] = widget

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        form_widget.setFixedWidth(280)

        # --- Middle: Image Upload ---
        image_layout = QVBoxLayout()
        image_label = QLabel("Upload Photo")
        image_label.setStyleSheet("color: white;")
        self.photo_display = QLabel()
        self.photo_display.setFixedSize(150, 200)
        self.photo_display.setStyleSheet("border: 2px dashed #00FFFF; background-color: #1e1e1e;")
        upload_btn = QPushButton("Upload Image")
        upload_btn.setStyleSheet("background-color: #00FFFF; font-weight: bold;")
        upload_btn.clicked.connect(self.upload_image)
        image_layout.addWidget(image_label)
        image_layout.addWidget(self.photo_display)
        image_layout.addWidget(upload_btn)
        image_layout.addStretch()
        image_widget = QWidget()
        image_widget.setLayout(image_layout)
        image_widget.setFixedWidth(180)

        # --- Right: Member Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "Address", "Status"])
        self.table.setStyleSheet("""
            QHeaderView::section { background-color: #00FFFF; color: black; }
            QTableWidget { background-color: #2A2A2A; color: white; font-size: 14px; border-radius: 10px; }
        """)
        self.table.setMinimumWidth(400)
        self.load_members()

        # Add all sections to content layout
        content_layout.addWidget(form_widget)
        content_layout.addWidget(image_widget)
        content_layout.addWidget(self.table)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)


    def upload_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            pixmap = QPixmap(file_name).scaled(150, 150, Qt.KeepAspectRatio)
            self.photo_display.setPixmap(pixmap)

    def load_members(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, phone, address, status FROM members")
            members = cursor.fetchall()
            self.table.setRowCount(len(members))
            for row_idx, row_data in enumerate(members):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
            conn.close()
        except Exception as e:
            print("Load members error:", e)

    def add_member(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            member_id = self.inputs["Member ID"].text()
            name = self.inputs["Name"].text()
            status = self.inputs["Status"].text()
            address = self.inputs["Address"].text()
            phone = self.inputs["Phone Number"].text()
            email = self.inputs["Email"].text()
            plan = self.inputs["Membership Plan"].text()
            start_date = self.inputs["Start Date"].text()
            total_billed = self.inputs["Total Billed"].text()

            cursor.execute("""
                INSERT INTO members (id, name, status, address, phone, email, membership_plan, start_date, total_billed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (member_id, name, status, address, phone, email, plan, start_date, total_billed))

            conn.commit()
            conn.close()
            self.load_members()
            print("Member added successfully.")
        except Exception as e:
            print("Add member error:", e)

    def update_member(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            member_id = self.inputs["Member ID"].text()
            name = self.inputs["Name"].text()
            status = self.inputs["Status"].text()
            address = self.inputs["Address"].text()
            phone = self.inputs["Phone Number"].text()
            email = self.inputs["Email"].text()
            plan = self.inputs["Membership Plan"].text()
            start_date = self.inputs["Start Date"].text()
            total_billed = self.inputs["Total Billed"].text()

            cursor.execute("""
                UPDATE members
                SET name=%s, status=%s, address=%s, phone=%s, email=%s,
                    membership_plan=%s, start_date=%s, total_billed=%s
                WHERE id=%s
            """, (name, status, address, phone, email, plan, start_date, total_billed, member_id))

            conn.commit()
            conn.close()
            self.load_members()
            print("Member updated successfully.")
        except Exception as e:
            print("Update member error:", e)

        self.table.cellClicked.connect(self.fill_form_from_table)

        def fill_form_from_table(self, row, _col):
            self.inputs["Member ID"].setText(self.table.item(row, 0).text())
            self.inputs["Name"].setText(self.table.item(row, 1).text())
            self.inputs["Email"].setText(self.table.item(row, 2).text())
            self.inputs["Phone Number"].setText(self.table.item(row, 3).text())
            self.inputs["Status"].setText(self.table.item(row, 5).text())


class SidebarButton(QPushButton):
    def __init__(self, icon_path, text):
        super().__init__(text)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #00FFFF;
                color: black;
            }
            QPushButton:checked {
                background-color: #00FFFF;
                color: black;
            }
        """)
        self.setCheckable(True)
        self.setAutoExclusive(True)

class StatsCard(QFrame):
    def __init__(self, title, icon_path, value):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border-left: 5px solid #00FFFF;
                border-radius: 10px;
            }
        """)
        self.setFixedHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QHBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        icon_label.setFixedSize(40, 40)

        text_layout = QVBoxLayout()
        label_title = QLabel(title)
        label_title.setStyleSheet("color: #AAAAAA; font-size: 14px;")
        self.label_value = QLabel(value)
        self.label_value.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")

        text_layout.addWidget(label_title)
        text_layout.addWidget(self.label_value)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        self.setLayout(layout)

    def set_value(self, value):
        self.label_value.setText(str(value))

class PieChartCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(facecolor='#2A2A2A')
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.plot_pie()

    def plot_pie(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT genre, COUNT(*) as count 
                FROM books 
                GROUP BY genre 
                ORDER BY count DESC 
                LIMIT 5
            """)
            data = cursor.fetchall()
            conn.close()

            genres = [row[0] for row in data]
            counts = [row[1] for row in data]

            self.ax.clear()
            self.ax.pie(
                counts,
                labels=genres,
                autopct='%1.1f%%',
                startangle=140,
                textprops={'color': 'white'}
            )
            self.ax.set_title("Top 5 Book Genres", color='white')
            self.draw()

        except Exception as e:
            print("Pie chart DB error:", e)
            self.ax.text(0.5, 0.5, "DB Error", color='white', ha='center')
            self.draw()

class BarChartCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(facecolor='#2A2A2A')
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.plot_bar()

    def plot_bar(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    MONTHNAME(issue_date) as month,
                    COUNT(*) as checkouts
                FROM transactions
                GROUP BY MONTH(issue_date)
                ORDER BY MONTH(issue_date)
            """)
            checkouts_data = cursor.fetchall()

            cursor.execute("""
                SELECT 
                    MONTHNAME(return_date) as month,
                    COUNT(*) as returns
                FROM transactions
                WHERE returned = 1
                GROUP BY MONTH(return_date)
                ORDER BY MONTH(return_date)
            """)
            returns_data = cursor.fetchall()

            conn.close()

            months = list(dict.fromkeys(
                [m[0] for m in checkouts_data] + [m[0] for m in returns_data]
            ))

            checkout_map = dict(checkouts_data)
            return_map = dict(returns_data)

            checkout_vals = [checkout_map.get(month, 0) for month in months]
            return_vals = [return_map.get(month, 0) for month in months]

            x = range(len(months))
            self.ax.clear()
            self.ax.bar(x, checkout_vals, width=0.4, label='Checkouts', color='#00FFFF')
            self.ax.bar([i + 0.4 for i in x], return_vals, width=0.4, label='Returns', color='orange')
            self.ax.set_xticks([i + 0.2 for i in x])
            self.ax.set_xticklabels(months, color='white')
            self.ax.set_title("Monthly Checkouts vs Returns", color='white')
            self.ax.legend()
            self.ax.tick_params(axis='y', colors='white')
            self.draw()

        except Exception as e:
            print("Bar chart DB error:", e)
            self.ax.text(0.5, 0.5, "DB Error", color='white', ha='center')
            self.draw()


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coddy Library")
        self.resize(1200,800)
        self.setMinimumSize(1000,700)
        self.setStyleSheet("background-color: #6d3f0a;")

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(10, 10, 10, 10)
        sidebar.setSpacing(15)

        self.buttons = []
        sidebar_buttons = [
            ("assets/icons/dashboard.png", "Dashboard (Home)"),
            ("assets/icons/members.png", "Members"),
            ("assets/icons/books.png", "Books"),
            ("assets/icons/borrow.png", "Borrow/Return"),
            ("assets/icons/fines.png", "Fines"),
            ("assets/icons/reports.png", "Reports"),
            ("assets/icons/setting.png", "Settings"),
            ("assets/icons/logout.png", "Logout")
        ]

        for i, (icon, label) in enumerate(sidebar_buttons):
            btn = SidebarButton(icon, label)
            if i == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, index=i: self.stack.setCurrentIndex(index))
            sidebar.addWidget(btn)
            self.buttons.append(btn)

        sidebar.addStretch()

        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setFixedWidth(220)
        sidebar_frame.setStyleSheet("background-color: #0a0f2c;")

        # Stack widget to hold different views
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_dashboard_page())  # index 0
        self.stack.addWidget(MembersPage())  # index 1

        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(self.stack)

    def create_dashboard_page(self):
        page = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Top bar
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search books, members…")
        search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #00FFFF;
                border-radius: 10px;
                color: white;
                background-color: #2E2E2E;
            }
        """)
        top_bar.addWidget(search_input)
        content_layout.addLayout(top_bar)

        stats_layout = QHBoxLayout()
        self.card_books = StatsCard("Total Books", "assets/icons/books.png", "0")
        self.card_loans = StatsCard("Active Loans", "assets/icons/borrow.png", "0")
        self.card_overdue = StatsCard("Overdue", "assets/icons/fines.png", "0")
        self.card_members = StatsCard("Members", "assets/icons/members.png", "0")

        stats_layout.addWidget(self.card_books)
        stats_layout.addWidget(self.card_loans)
        stats_layout.addWidget(self.card_overdue)
        stats_layout.addWidget(self.card_members)
        content_layout.addLayout(stats_layout)

        self.update_stats()

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Timestamp", "Activity"])
        table.setStyleSheet("""
            QHeaderView::section {
                background-color: #00FFFF;
                color: black;
            }
            QTableWidget {
                background-color: #2A2A2A;
                color: white;
                font-size: 14px;
                border-radius: 10px;
            }
        """)
        table.setRowCount(5)
        sample_data = [
            ("2025-06-15 10:22", "John returned 'The Hobbit'"),
            ("2025-06-15 09:45", "Anna borrowed '1984'"),
            ("2025-06-15 09:10", "Mark returned 'Python 101'"),
            ("2025-06-15 08:35", "Jane borrowed 'Atomic Habits'"),
            ("2025-06-15 08:00", "Paul returned 'Data Science Handbook'")
        ]
        for i, (ts, activity) in enumerate(sample_data):
            table.setItem(i, 0, QTableWidgetItem(ts))
            table.setItem(i, 1, QTableWidgetItem(activity))

        content_layout.addSpacing(30)
        content_layout.addWidget(QLabel("Recent Activity", styleSheet="color: white; font-size: 18px;"))
        content_layout.addWidget(table)

        chart_layout = QHBoxLayout()
        pie_chart = PieChartCanvas()
        bar_chart = BarChartCanvas()
        chart_layout.addWidget(pie_chart)
        chart_layout.addWidget(bar_chart)

        content_layout.addSpacing(20)
        content_layout.addLayout(chart_layout)

        page.setLayout(content_layout)
        return page

    def update_stats(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transactions WHERE returned = 0")
        active_loans = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transactions WHERE returned = 0 AND return_date < CURDATE()")
        overdue = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM members")
        members = cursor.fetchone()[0]

        conn.close()

        self.card_books.set_value(total_books)
        self.card_loans.set_value(active_loans)
        self.card_overdue.set_value(overdue)
        self.card_members.set_value(members)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
