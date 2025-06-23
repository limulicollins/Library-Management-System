from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from db_config import get_connection
from PyQt5.QtGui import QPixmap
from style import shared_stylesheet

class BorrowReturnPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setStyleSheet(shared_stylesheet)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

       # === Title with Logo ===
        title_bar = QHBoxLayout()

        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/icons/borrow.png")
        logo_label.setPixmap(logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(36, 36)

        title = QLabel("Borrow & Return")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)

        title_bar.addWidget(logo_label)
        title_bar.addWidget(title)
        title_bar.addStretch()

        layout.addLayout(title_bar)


        # === Search section ===
        search_layout = QHBoxLayout()

        self.member_input = QLineEdit()
        self.member_input.setPlaceholderText("Enter Member ID")
        search_layout.addWidget(self.member_input)

        self.book_input = QLineEdit()
        self.book_input.setPlaceholderText("Enter Book ISBN")
        search_layout.addWidget(self.book_input)

        self.search_button = QPushButton("Load Info")
        self.search_button.clicked.connect(self.load_info)
        search_layout.addWidget(self.search_button)

        layout.addLayout(search_layout)

        # === Info Section ===
        info_layout = QHBoxLayout()

        self.member_info = QLabel("Member: ")
        self.member_info.setStyleSheet("font-size: 16px; font-weight: bold; color: #00FFFF;")
        self.book_info = QLabel("Book: ")
        self.book_info.setStyleSheet("font-size: 16px; font-weight: bold; color: #00FFFF;")
        info_layout.addWidget(self.member_info)
        info_layout.addWidget(self.book_info)

        layout.addLayout(info_layout)

        # === Date Pickers ===
        date_layout = QHBoxLayout()

        self.borrow_date = QDateEdit(QDate.currentDate())
        self.borrow_date.setCalendarPopup(True)
        date_layout.addWidget(QLabel("Borrow Date:"))
        date_layout.addWidget(self.borrow_date)

        self.return_date = QDateEdit(QDate.currentDate().addDays(14))
        self.return_date.setCalendarPopup(True)
        date_layout.addWidget(QLabel("Return Date:"))
        date_layout.addWidget(self.return_date)

        layout.addLayout(date_layout)

        # === Action Buttons ===
        action_layout = QHBoxLayout()

        self.borrow_button = QPushButton("Borrow")
        self.borrow_button.clicked.connect(self.borrow_book)
        action_layout.addWidget(self.borrow_button)

        self.return_button = QPushButton("Return")
        self.return_button.clicked.connect(self.return_book)
        action_layout.addWidget(self.return_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_fields)
        action_layout.addWidget(self.clear_button)

        layout.addLayout(action_layout)

        # === Loan Table ===
        self.loan_table = QTableWidget()
        self.loan_table.setColumnCount(4)
        self.loan_table.setHorizontalHeaderLabels(["Book", "Issue Date", "Return Date", "Returned"])
        layout.addWidget(self.loan_table)

        self.setLayout(layout)

    def load_info(self):
        member_id = self.member_input.text().strip()
        isbn = self.book_input.text().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Load member
            cursor.execute("SELECT name, email FROM members WHERE id = %s", (member_id,))
            member = cursor.fetchone()
            if member:
                self.member_info.setText(f"Member: {member[0]} ({member[1]})")
            else:
                self.member_info.setText("Member not found")
                return

            # Load book
            cursor.execute("SELECT title, copies FROM books WHERE isbn = %s", (isbn,))
            book = cursor.fetchone()
            if book:
                self.book_info.setText(f"Book: {book[0]} (Available: {book[1]})")
            else:
                self.book_info.setText("Book not found")
                return

            # Load active loans
            cursor.execute("""
                SELECT b.title, t.issue_date, t.return_date, t.returned
                FROM transactions t
                JOIN books b ON t.book_id = b.id
                WHERE t.member_id = %s
                ORDER BY t.issue_date DESC
            """, (member_id,))
            rows = cursor.fetchall()

            self.loan_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.loan_table.setItem(i, j, QTableWidgetItem(str(val)))

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load info:\n{e}")

    def borrow_book(self):
        member_id = self.member_input.text().strip()
        isbn = self.book_input.text().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Get book ID and copies
            cursor.execute("SELECT id, copies FROM books WHERE isbn = %s", (isbn,))
            book = cursor.fetchone()
            if not book:
                QMessageBox.warning(self, "Error", "Book not found")
                return
            book_id, copies = book
            if copies < 1:
                QMessageBox.warning(self, "Unavailable", "No copies available")
                return

            # Check member exists
            cursor.execute("SELECT id FROM members WHERE id = %s", (member_id,))
            if not cursor.fetchone():
                QMessageBox.warning(self, "Error", "Member not found")
                return

            # Borrow book
            cursor.execute("""
                INSERT INTO transactions (book_id, member_id, issue_date, return_date, returned)
                VALUES (%s, %s, %s, %s, 0)
            """, (
                book_id,
                member_id,
                self.borrow_date.date().toString("yyyy-MM-dd"),
                self.return_date.date().toString("yyyy-MM-dd")
            ))

            cursor.execute("UPDATE books SET copies = copies - 1 WHERE id = %s", (book_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Book borrowed successfully")
            self.load_info()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to borrow:\n{e}")

    def return_book(self):
        member_id = self.member_input.text().strip()
        isbn = self.book_input.text().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Get book ID
            cursor.execute("SELECT id FROM books WHERE isbn = %s", (isbn,))
            book = cursor.fetchone()
            if not book:
                QMessageBox.warning(self, "Error", "Book not found")
                return
            book_id = book[0]

            # Mark transaction as returned
            cursor.execute("""
                UPDATE transactions 
                SET returned = 1 
                WHERE member_id = %s AND book_id = %s AND returned = 0
                ORDER BY issue_date ASC LIMIT 1
            """, (member_id, book_id))

            if cursor.rowcount == 0:
                QMessageBox.information(self, "Notice", "No active loan found for this member/book.")
            else:
                cursor.execute("UPDATE books SET copies = copies + 1 WHERE id = %s", (book_id,))
                QMessageBox.information(self, "Success", "Book returned successfully")

            conn.commit()
            conn.close()
            self.load_info()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to return:\n{e}")

    def clear_fields(self):
        self.member_input.clear()
        self.book_input.clear()
        self.member_info.setText("Member: ")
        self.book_info.setText("Book: ")
        self.loan_table.setRowCount(0)
