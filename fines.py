from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime
from style import shared_stylesheet


class FinesPage(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.setStyleSheet(shared_stylesheet)
        self.init_ui()

    def init_ui(self):
        
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        # Top Bar
        title_bar = QHBoxLayout()
        title = QLabel("📄 Fines Management")
        title.setStyleSheet("padding: 10px; color: white; font-weight: bold; font-size: 20px;")
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search by member/book/date")
        filter_box = QComboBox()
        filter_box.addItems(["All", "Paid", "Unpaid"])
        export_btn = QPushButton("Export")

        title_bar.addWidget(title)
        title_bar.addStretch()
        title_bar.addWidget(search_input)
        title_bar.addWidget(filter_box)
        title_bar.addWidget(export_btn)

        # Fines Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Fine ID", "Member", "Book", "Due Date", "Return Date",
            "Days Late", "Amount (KSH)", "Status", "Action"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        left_layout.addLayout(title_bar)
        left_layout.addWidget(self.table)

        # Right-side Details
        self.details_box = QGroupBox("Fine Details")
        details_layout = QVBoxLayout()

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)

        self.pay_btn = QPushButton("Mark as Paid")
        self.pay_btn.setVisible(False)  # Show only for unpaid fines

        details_layout.addWidget(self.details_text)
        details_layout.addWidget(self.pay_btn)
        self.details_box.setLayout(details_layout)

        main_layout.addLayout(left_layout, 3)
        main_layout.addWidget(self.details_box, 2)

        self.setLayout(main_layout)

        # Connect events
        self.table.cellClicked.connect(self.show_details)
        self.pay_btn.clicked.connect(self.mark_as_paid)
        export_btn.clicked.connect(self.export_fines)

        # Load data
        self.load_fines()

    def load_fines(self):
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                t.id AS fine_id,
                m.name AS member_name,
                b.title AS book_title,
                t.due_date,
                t.return_date,
                t.returned
            FROM transactions t
            JOIN members m ON t.member_id = m.id
            JOIN books b ON t.book_id = b.id
            WHERE t.returned = 1
        """)
        records = cursor.fetchall()
        self.table.setRowCount(0)

        fine_rate = 50  # KSH per day

        for row_num, row_data in enumerate(records):
            fine_id, member, book, due_date, return_date, returned = row_data

            if not due_date:
                print(f"Skipping fine {fine_id} due to missing due date.")
                continue

            try:
                due_dt = datetime.strptime(str(due_date), "%Y-%m-%d")

                if return_date:
                    ret_dt = datetime.strptime(str(return_date), "%Y-%m-%d")
                else:
                    ret_dt = datetime.today()

                days_late = max((ret_dt - due_dt).days, 0)
                fine_amount = days_late * fine_rate
                status = "Unpaid" if fine_amount > 0 else "Paid"

                self.table.insertRow(row_num)
                values = [
                    fine_id,
                    member,
                    book,
                    str(due_date),
                    str(return_date) if return_date else "Not Returned",
                    str(days_late),
                    str(fine_amount),
                    status
                ]

                for col, value in enumerate(values):
                    self.table.setItem(row_num, col, QTableWidgetItem(str(value)))

                btn = QPushButton("Mark Paid" if status == "Unpaid" else "✓")
                btn.setEnabled(status == "Unpaid")
                btn.clicked.connect(lambda _, fid=fine_id: self.mark_as_paid(fid))
                self.table.setCellWidget(row_num, 8, btn)

            except Exception as e:
                print(f"Error processing fine {fine_id}: {e}")
                continue

        cursor.close()

    def show_details(self, row, column):
        fine_id = self.table.item(row, 0).text()
        member = self.table.item(row, 1).text()
        book = self.table.item(row, 2).text()
        due = self.table.item(row, 3).text()
        ret = self.table.item(row, 4).text()
        days = self.table.item(row, 5).text()
        amount = self.table.item(row, 6).text()
        status = self.table.item(row, 7).text()

        details = f"""
Fine ID: {fine_id}
Member: {member}
Book: {book}
Due Date: {due}
Return Date: {ret}
Days Overdue: {days}
Fine Amount: {amount} KSH
Status: {status}
        """.strip()

        self.details_text.setText(details)
        self.pay_btn.setVisible(status == "Unpaid")

    def mark_as_paid(self, fine_id):
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE transactions
                SET fine_paid = TRUE
                WHERE id = %s
            """, (fine_id,))
            self.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", f"Fine {fine_id} marked as paid.")
            self.load_fines()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error:\n{e}")

    def export_fines(self):
        # Placeholder: export logic (to CSV or PDF)
        QMessageBox.information(self, "Export", "Fines exported successfully.")
