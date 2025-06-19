from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QTableWidget, QDateEdit
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys
from db_config import get_connection


class MembersPage(QWidget):
    def __init__(self):
        super().__init__()

        # ---------- MAIN LAYOUT ----------
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ---------- TOP: TITLE + SEARCH ----------
        top_layout = QHBoxLayout()
        title = QLabel("Members Management")
        title.setStyleSheet("color: white; font-size: 30px;")
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search by name or ID")
        search_bar.setStyleSheet(
            "padding: 8px; font-size: 14px; border: 2px solid #00FFFF;"
            "border-radius: 10px; color: white; background-color: #2E2E2E;"
        )
        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(search_bar)
        main_layout.addLayout(top_layout)

        # ---------- BUTTON BAR ----------
        button_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_update = QPushButton("Update")
        self.btn_delete = QPushButton("Delete")
        self.btn_clear = QPushButton("Clear")
        self.btn_export = QPushButton("Export")

        self.btn_add.clicked.connect(self.add_member)
        self.btn_update.clicked.connect(self.update_member)
        # TODO: connect delete / clear / export as needed

        for btn in [
            self.btn_add, self.btn_update, self.btn_delete,
            self.btn_clear, self.btn_export
        ]:
            btn.setStyleSheet(
                "background-color: #00FFFF; color: black; font-weight: bold;"
                "padding: 10px; border-radius: 8px;"
            )
            button_layout.addWidget(btn)

        main_layout.addLayout(button_layout)        # ✅ added AFTER button_layout is defined

        # ---------- CONTENT AREA ----------
        content_layout = QHBoxLayout()

        # ----- Form -----
        form_layout = QVBoxLayout()

        def create_input(label_text):
            label = QLabel(label_text)
            label.setStyleSheet("color: white;")
            input_field = QLineEdit()
            input_field.setStyleSheet(
                "background-color: #2E2E2E; color: white; padding: 10px; border-radius: 10px;"
            )
            return label, input_field

        fields = [
            "Member ID", "Name", "Status", "Address", "Phone Number",
            "Email", "Membership Plan", "Start Date", "Total Billed"
        ]
        self.inputs = {}
        for field in fields:
            label, widget = create_input(field)
            form_layout.addWidget(label)
            form_layout.addWidget(widget)
            self.inputs[field] = widget

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        form_widget.setFixedWidth(280)

        # ----- Image Upload -----
        image_layout = QVBoxLayout()
        image_label = QLabel("Upload Photo")
        image_label.setStyleSheet("color: white;")
        self.photo_display = QLabel()
        self.photo_display.setFixedSize(150, 200)
        self.photo_display.setStyleSheet(
            "border: 2px dashed #00FFFF; background-color: #1e1e1e;"
        )
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

        # ----- Member Table -----
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Email", "Phone", "Address", "Status"]
        )
        self.table.setStyleSheet(
            """
            QHeaderView::section { background-color: #00FFFF; color: black; }
            QTableWidget { background-color: #2A2A2A; color: white;
                           font-size: 14px; border-radius: 10px; }
            """
        )
        self.table.setMinimumWidth(400)
        self.table.cellClicked.connect(self.fill_form_from_table)  # ✅ connected once
        self.load_members()

        # ----- Assemble content area -----
        content_layout.addWidget(form_widget)
        content_layout.addWidget(image_widget)
        content_layout.addWidget(self.table)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    # ---------- Helper Methods ----------
    def upload_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)"
        )
        if file_name:
            pixmap = QPixmap(file_name).scaled(150, 150, Qt.KeepAspectRatio)
            self.photo_display.setPixmap(pixmap)

    def load_members(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email, phone, address, status FROM members"
            )
            members = cursor.fetchall()
            self.table.setRowCount(len(members))
            for row_idx, row_data in enumerate(members):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(
                        row_idx, col_idx, QTableWidgetItem(str(col_data))
                    )
            conn.close()
        except Exception as e:
            print("Load members error:", e)

    def add_member(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            data = (
                self.inputs["Member ID"].text(),
                self.inputs["Name"].text(),
                self.inputs["Status"].text(),
                self.inputs["Address"].text(),
                self.inputs["Phone Number"].text(),
                self.inputs["Email"].text(),
                self.inputs["Membership Plan"].text(),
                self.inputs["Start Date"].text(),
                self.inputs["Total Billed"].text(),
            )
            cursor.execute(
                """
                INSERT INTO members
                (id, name, status, address, phone, email,
                 membership_plan, start_date, total_billed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                data,
            )
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
            data = (
                self.inputs["Name"].text(),
                self.inputs["Status"].text(),
                self.inputs["Address"].text(),
                self.inputs["Phone Number"].text(),
                self.inputs["Email"].text(),
                self.inputs["Membership Plan"].text(),
                self.inputs["Start Date"].text(),
                self.inputs["Total Billed"].text(),
                self.inputs["Member ID"].text(),  # WHERE id = ?
            )
            cursor.execute(
                """
                UPDATE members
                SET name=%s, status=%s, address=%s, phone=%s, email=%s,
                    membership_plan=%s, start_date=%s, total_billed=%s
                WHERE id=%s
                """,
                data,
            )
            conn.commit()
            conn.close()
            self.load_members()
            print("Member updated successfully.")
        except Exception as e:
            print("Update member error:", e)

    def fill_form_from_table(self, row, _col):
        """Populate the form fields when a row is clicked."""
        self.inputs["Member ID"].setText(self.table.item(row, 0).text())
        self.inputs["Name"].setText(self.table.item(row, 1).text())
        self.inputs["Email"].setText(self.table.item(row, 2).text())
        self.inputs["Phone Number"].setText(self.table.item(row, 3).text())
        self.inputs["Address"].setText(self.table.item(row, 4).text())
        self.inputs["Status"].setText(self.table.item(row, 5).text())


# ---------- Stand‑alone test ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MembersPage()
    win.show()
    sys.exit(app.exec_())
