from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QFrame, QSizePolicy, QStackedWidget
)
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtCore import Qt, QSize
import sys
import os
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from db_config import get_connection
from members import MembersPage
from books import BooksPage
from PyQt5.QtGui import QMovie
from borrow_return import BorrowReturnPage
from fines import FinesPage
from style import shared_stylesheet

class SidebarButton(QPushButton):
    def __init__(self, icon_path, text):
        super().__init__(text)
        self.setStyleSheet(shared_stylesheet)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        self.setCheckable(True)
        self.setAutoExclusive(True)

class StatsCard(QFrame):
    def __init__(self, title, icon_path, value):
        super().__init__()
        self.setFixedHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QHBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        icon_label.setFixedSize(40, 40)

        text_layout = QVBoxLayout()
        label_title = QLabel(title)
        self.label_value = QLabel(value)

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
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.setWindowTitle("📚 Coddy Library Management System 📚")
        self.resize(1200,800)
        self.setMinimumSize(1000,700)
        self.setStyleSheet(shared_stylesheet)
        self.setStyleSheet("background-color: #0a0f2c;")

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
        self.stack.addWidget(MembersPage()) 
        self.stack.addWidget(BooksPage()) # index 1
        self.stack.addWidget(BorrowReturnPage()) #index 2
        self.stack.addWidget(FinesPage(self.db_connection))  # index 3

        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(self.stack)

    def create_dashboard_page(self):
        page = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Top bar with search + refresh
        top_bar = QHBoxLayout()
        welcome_label = QLabel("Welcome to Coddy Library Dashboard")
        welcome_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        top_bar.addWidget(welcome_label)
        top_bar.addStretch()

        search_input = QLineEdit()
        search_input.setPlaceholderText("Search books, members…")
        top_bar.addWidget(search_input)

        refresh_button = QPushButton("♻️")
        refresh_button.clicked.connect(self.update_stats)
        top_bar.addWidget(refresh_button)
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

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Timestamp", "Activity"])
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
        self.pie_chart = PieChartCanvas()
        self.bar_chart = BarChartCanvas()
        chart_layout.addWidget(self.pie_chart)
        chart_layout.addWidget(self.bar_chart)

        content_layout.addSpacing(20)
        content_layout.addLayout(chart_layout)

        self.update_stats()

        page.setLayout(content_layout)
        return page

    def update_stats(self):
        try:
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
            self.pie_chart.plot_pie()
            self.bar_chart.plot_bar()


        except Exception as e:
            print("Error updating stats:", e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
