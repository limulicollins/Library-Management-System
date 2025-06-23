from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from db_config import get_connection
import shutil
import os
from style import shared_stylesheet

class BooksPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(shared_stylesheet)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ─── Top: Title + Search ───
        top_layout = QHBoxLayout()
        title = QLabel("Books Management")

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by title, author, or ISBN")
        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(self.search_bar)
        main_layout.addLayout(top_layout)

        GENRES = ["Biography", "History", "Science", "Technology", "Business", "Economics", "Coding", "Mathematics", "Literature", "Physics"]

        # ─── Buttons ───
        button_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_update = QPushButton("Update")
        self.btn_delete = QPushButton("Delete")
        self.btn_clear = QPushButton("Clear")
        self.btn_export = QPushButton("Export")

        for btn in [self.btn_add, self.btn_update, self.btn_delete, self.btn_clear, self.btn_export]:
            button_layout.addWidget(btn)

        main_layout.addLayout(button_layout)
        self.btn_add.clicked.connect(self.add_book)
        self.btn_update.clicked.connect(self.update_book)
        self.btn_delete.clicked.connect(self.delete_book)
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_export.clicked.connect(self.export_books)
        self.search_bar.textChanged.connect(self.search_books)


        # ─── Content: Form + Table ───
        content_layout = QHBoxLayout()
        form_layout = QVBoxLayout()

        self.inputs = {}

        def add_form_field(label_text, is_disabled=False):
            label = QLabel(label_text)
            label.setStyleSheet("color: white;")
            input_field = QLineEdit()
            if is_disabled:
                input_field.setReadOnly(True)
            else:
                input_field.setStyleSheet("background-color: #2E2E2E; color: white; padding: 10px; border-radius: 10px;")
            form_layout.addWidget(label)
            form_layout.addWidget(input_field)
            self.inputs[label_text] = input_field

        add_form_field("ID", is_disabled=True)  # Auto-generated
        add_form_field("Title")
        add_form_field("Author")
        add_form_field("ISBN")
        label = QLabel("Genre")
        label.setStyleSheet("color: white;")
        self.genre_dropdown = QComboBox()
        self.genre_dropdown.addItems(GENRES)
        form_layout.addWidget(label)
        form_layout.addWidget(self.genre_dropdown)
        add_form_field("Copies")

        # ─── Book Cover Upload (Below form) ───
        img_label = QLabel("Book Cover")
        img_label.setStyleSheet("color: white;")
        self.cover_display = QLabel()
        self.cover_display.setFixedSize(150, 200)
        upload_btn = QPushButton("Upload Cover")
        upload_btn.clicked.connect(self.upload_cover)

        form_layout.addWidget(img_label)
        form_layout.addWidget(self.cover_display)
        form_layout.addWidget(upload_btn)
        form_layout.addStretch()

        content_layout.addLayout(form_layout)

        # ─── Book Table ───
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Author", "ISBN", "Genre", "Copies", "Cover_path"])
        content_layout.addWidget(self.table)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)
        self.load_books()
        self.table.cellClicked.connect(self.fill_form_from_table)
        self.cover_path = ""

    def fill_form_from_table(self, row, _col):
        self.inputs["ID"].setText(self.table.item(row, 0).text())
        self.inputs["Title"].setText(self.table.item(row, 1).text())
        self.inputs["Author"].setText(self.table.item(row, 2).text())
        self.inputs["ISBN"].setText(self.table.item(row, 3).text())
        genre = self.table.item(row, 4).text()
        index = self.genre_dropdown.findText(genre)
        if index >= 0:
            self.genre_dropdown.setCurrentIndex(index)
            self.genre_dropdown.setCurrentIndex(0)
        self.inputs["Copies"].setText(self.table.item(row, 5).text())
        cover_path = self.table.item(row, 6).text() if self.table.columnCount() > 6 else ""
        if cover_path:
            pixmap = QPixmap(cover_path).scaled(150, 200, Qt.KeepAspectRatio)
            self.cover_display.setPixmap(pixmap)
        else:
            self.cover_display.clear()

    def upload_cover(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Cover Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_name:
            # Step 1: Ensure 'assets/covers/' exists
            cover_dir = os.path.join("assets", "covers")
            if not os.path.exists(cover_dir):
                os.makedirs(cover_dir)

            # Step 2: Generate a unique, readable file name
            title = self.inputs["Title"].text().strip().replace(" ", "_")
            isbn = self.inputs["ISBN"].text().strip().replace(" ", "_")
            ext = os.path.splitext(file_name)[1]  # keeps .jpg or .png
            dest_filename = f"{title}_{isbn}{ext}"
            dest_path = os.path.join(cover_dir, dest_filename)

            # Step 3: Copy image to destination
            shutil.copy(file_name, dest_path)

            # Step 4: Save the relative path for DB storage
            self.cover_path = dest_path

            # Step 5: Show the image in the UI
            pixmap = QPixmap(dest_path).scaled(150, 200, Qt.KeepAspectRatio)
            self.cover_display.setPixmap(pixmap)


    def load_books(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author, isbn, genre, copies, cover_path FROM books")
            books = cursor.fetchall()
            self.table.setRowCount(len(books))
            for row_idx, row_data in enumerate(books):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
            conn.close()
        except Exception as e:
            print("Load books error:", e)


    def add_book(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            title = self.inputs["Title"].text()
            author = self.inputs["Author"].text()
            isbn = self.inputs["ISBN"].text()
            genre = self.genre_dropdown.currentText()
            copies = self.inputs["Copies"].text()
            cover_path = self.cover_path if hasattr(self, "cover_path") else ""

            if not (title and author and isbn and genre and copies):
                print("Please fill all fields.")
                return

            cursor.execute("""
                INSERT INTO books (title, author, isbn, genre, copies, cover_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, author, isbn, genre, copies, cover_path))

            conn.commit()
            conn.close()

            self.load_books()
            print("Book added successfully.")

            # Optional: Clear form
            for field in self.inputs:
                if field != "ID":
                    self.inputs[field].clear()
            self.cover_display.clear()

        except Exception as e:
            print("Add book error:", e)

    def update_book(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            book_id = self.inputs["ID"].text()
            title = self.inputs["Title"].text()
            author = self.inputs["Author"].text()
            isbn = self.inputs["ISBN"].text()
            genre = self.genre_dropdown.currentText()
            copies = self.inputs["Copies"].text()

            if not book_id:
                print("No book selected to update.")
                return

            cursor.execute("""
                UPDATE books
                SET title=%s, author=%s, isbn=%s, genre=%s, copies=%s
                WHERE id=%s
            """, (title, author, isbn, genre, copies, book_id))

            conn.commit()
            conn.close()

            self.load_books()
            print("Book updated successfully.")
        
        # Optional: Clear form after update
            for field in self.inputs:
                if field != "ID":
                    self.inputs[field].clear()
            self.cover_display.clear()

        except Exception as e:
            print("Update book error:", e)

    def delete_book(self):
        try:
            book_id = self.inputs["ID"].text()

            if not book_id:
                print("No book selected to delete.")
                return

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
            conn.commit()
            conn.close()

            self.load_books()
            print("Book deleted successfully.")

        # Optional: Clear form
            for field in self.inputs:
                if field != "ID":
                    self.inputs[field].clear()
            self.cover_display.clear()
            self.genre_dropdown.setCurrentIndex(0)

        except Exception as e:
            print("Delete book error:", e)

    def clear_form(self):
        for field in self.inputs:
            if field != "ID":
                self.inputs[field].clear()

        self.genre_dropdown.setCurrentIndex(0)
        self.cover_display.clear()
        self.table.clearSelection()

    def export_books(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Books", "", "CSV Files (*.csv)")

        if not path:
            return  # Cancelled

        try:
            with open(path, "w", encoding="utf-8") as file:
                headers = ["ID", "Title", "Author", "ISBN", "Genre", "Copies"]
                file.write(",".join(headers) + "\n")

                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    file.write(",".join(row_data) + "\n")

            print(f"Books exported to {path}")
        except Exception as e:
            print("Export error:", e)

    def search_books(self):
        query = self.search_bar.text().lower()

        for row in range(self.table.rowCount()):
            title = self.table.item(row, 1).text().lower()
            author = self.table.item(row, 2).text().lower()
            isbn = self.table.item(row, 3).text().lower()

            if query in title or query in author or query in isbn:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
