from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QDateEdit, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys
from db_config import get_connection
import os
import shutil
from datetime import datetime
from PIL import Image

class MembersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.inputs = {}
        self.inputs["Photo Path"] = "" 
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- Top Section: Title and Search ---
        top_layout = QHBoxLayout()
        title = QLabel("Members Management")
        title.setStyleSheet("color: #00FFFF; font-size: 30px;")
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by name or ID")
        self.search_bar.setStyleSheet(
            "padding: 8px; font-size: 14px; border: 2px solid #00FFFF;"
            "border-radius: 10px; color: white; background-color: #2E2E2E;"
        )
        self.search_bar.textChanged.connect(self.search_member)
        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(self.search_bar)
        main_layout.addLayout(top_layout)

        # --- Button Bar ---
        button_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_update = QPushButton("Update")
        self.btn_delete = QPushButton("Delete")
        self.btn_clear = QPushButton("Clear")
        self.btn_export = QPushButton("Export")

        for btn in [self.btn_add, self.btn_update, self.btn_delete, self.btn_clear, self.btn_export]:
            btn.setStyleSheet("background-color: #00FFFF; color: black; font-weight: bold; padding: 10px; border-radius: 8px;")
            button_layout.addWidget(btn)

        self.btn_add.clicked.connect(self.add_member)
        self.btn_update.clicked.connect(self.update_member)
        self.btn_delete.clicked.connect(self.delete_member)
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_export.clicked.connect(self.export_data)
        main_layout.addLayout(button_layout)

        # --- Content Area ---
        content_layout = QHBoxLayout()

        # --- Left: Form ---
        form_layout = QVBoxLayout()
        fields = [
            "Member ID", "Name", "Address", "Phone Number",
            "Email", "Membership Plan", "Start Date", "Total Billed"
        ]

        for field in fields:
            label = QLabel(field)
            label.setStyleSheet("color: white;")

            if field == "Membership Plan":
                widget = QComboBox()
                widget.setStyleSheet("background-color: #2E2E2E; color: white; padding: 10px; border-radius: 10px;")
                self.load_membership_plans(widget)

            elif field == "Start Date":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setStyleSheet("background-color: #2E2E2E; color: white; padding: 10px; border-radius: 10px;")

            else:
                widget = QLineEdit()
                widget.setStyleSheet("background-color: #2E2E2E; color: white; padding: 10px; border-radius: 10px;")
                if field == "Member ID":
                    widget.setReadOnly(True)
                    widget.setText(self.generate_member_id())

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

        # --- Right: Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "Address", "Membership Plan", "Start Date", "Total Billed"])
        self.table.setStyleSheet("""
            QHeaderView::section { background-color: #00FFFF; color: black; }
            QTableWidget { background-color: #2A2A2A; color: white; font-size: 14px; border-radius: 10px; }
        """)
        self.table.setMinimumWidth(400)
        self.table.cellClicked.connect(self.fill_form_from_table)
        self.load_members()

        content_layout.addWidget(form_widget)
        content_layout.addWidget(image_widget)
        content_layout.addWidget(self.table)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    def generate_member_id(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM members")
            count = cursor.fetchone()[0] + 1
            conn.close()
            return f"M{count:03}"
        except Exception as e:
            print("ID generation error:", e)
            return "M001"

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.bmp *.jpeg)"
        )
        if file_path:
                # Create directory if not exists
            save_dir = "assets/members"
            os.makedirs(save_dir, exist_ok=True)

            # Generate unique filename
            ext = os.path.splitext(file_path)[1]
            filename = f"{self.inputs['Member ID'].text()}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            dest_path = os.path.join(save_dir, filename)

            try:
                shutil.copy(file_path, dest_path)
                img = Image.open(file_path)
                img.thumbnail((300, 400))  # Resize image for storage
                img.save(dest_path)
                self.photo_display.setPixmap(QPixmap(dest_path).scaled(150, 200, Qt.KeepAspectRatio))
                self.inputs["Photo Path"] = dest_path  # Store path internally
            except Exception as e:
                print("Image upload failed:", e)

    def load_members(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, phone, address, membership_plan, start_date, total_billed FROM members")
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
            data = (
                self.inputs["Member ID"].text(),
                self.inputs["Name"].text(),
                self.inputs["Address"].text(),
                self.inputs["Phone Number"].text(),
                self.inputs["Email"].text(),
                self.inputs["Membership Plan"].currentText(),
                self.inputs["Start Date"].date().toString("yyyy-MM-dd"),
                self.inputs["Total Billed"].text()
            )
            cursor.execute("""
                INSERT INTO members (id, name, address, phone, email, membership_plan, start_date, total_billed, photo_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, data + (self.inputs["Photo Path"],))
            conn.commit()
            conn.close()
            self.load_members()
            self.clear_form()
            print("Member added successfully.")
        except Exception as e:
            print("Add member error:", e)

    def update_member(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            data = (
                self.inputs["Name"].text(),
                self.inputs["Address"].text(),
                self.inputs["Phone Number"].text(),
                self.inputs["Email"].text(),
                self.inputs["Membership Plan"].currentText(),
                self.inputs["Start Date"].date().toString("yyyy-MM-dd"),
                self.inputs["Total Billed"].text(),
            )
            cursor.execute("""
                UPDATE members SET name=%s, address=%s, phone=%s, email=%s, membership_plan=%s, start_date=%s, total_billed=%s, photo_path=%s
                WHERE id=%s
            """, data + (self.inputs["Photo Path"], self.inputs["Member ID"].text()))
            conn.commit()
            conn.close()
            self.load_members()
            print("Member updated successfully.")
        except Exception as e:
            print("Update member error:", e)

    def delete_member(self):
        try:
            member_id = self.inputs["Member ID"].text()
            if not member_id:
                print("No member selected.")
                return
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM members WHERE id=%s", (member_id,))
            conn.commit()
            conn.close()
            self.load_members()
            self.clear_form()
            print("Member deleted.")
        except Exception as e:
            print("Delete member error:", e)

    def clear_form(self):
        for label, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                widget.clear()
                if label == "Member ID":
                    widget.setText(self.generate_member_id())
            elif isinstance(widget, QDateEdit):
                widget.setDate(widget.minimumDate())
        self.photo_display.clear()
        self.inputs["Photo Path"] = ""
        self.inputs["Membership Plan"].setCurrentIndex(0)

    def export_data(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Export Members", "", "CSV Files (*.csv)")
            if not file_path:
                return
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members")
            rows = cursor.fetchall()
            conn.close()
            with open(file_path, "w") as file:
                for row in rows:
                    file.write(",".join([str(cell) for cell in row]) + "\n")
            print("Exported successfully to:", file_path)
        except Exception as e:
            print("Export error:", e)

    def fill_form_from_table(self, row, _col):
        self.inputs["Member ID"].setText(self.table.item(row, 0).text())
        self.inputs["Name"].setText(self.table.item(row, 1).text())
        self.inputs["Email"].setText(self.table.item(row, 2).text())
        self.inputs["Phone Number"].setText(self.table.item(row, 3).text())
        self.inputs["Address"].setText(self.table.item(row, 4).text())
        self.inputs["Membership Plan"].setCurrentText(self.table.item(row, 5).text())
        self.inputs["Start Date"].setDate(self.inputs["Start Date"].minimumDate())
        self.inputs["Total Billed"].setText(self.table.item(row, 7).text())

        member_id = self.table.item(row, 0).text()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT photo_path FROM members WHERE id = %s", (member_id,))
            result = cursor.fetchone()
            if result and result[0] and os.path.exists(result[0]):
                self.photo_display.setPixmap(QPixmap(result[0]).scaled(150, 200, Qt.KeepAspectRatio))
                self.inputs["Photo Path"] = result[0]
            else:
                self.photo_display.clear()
                self.inputs["Photo Path"] = ""
            conn.close()
        except Exception as e:
            print("Failed to load photo:", e)

    def search_member(self):
        keyword = self.search_bar.text().strip()
        if not keyword:
            self.load_members()
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                SELECT id, name, email, phone, address, membership_plan, start_date, total_billed
                FROM members
                WHERE id LIKE %s OR name LIKE %s
            """
            param = (f"%{keyword}%", f"%{keyword}%")
            cursor.execute(query, param)
            results = cursor.fetchall()
            conn.close()

            self.table.setRowCount(len(results))
            for row_idx, row_data in enumerate(results):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        except Exception as e:
            print("Search error:", e)

    def load_membership_plans(self, combo):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_type, access_level, duration, price FROM membership_plans")
            plans = cursor.fetchall()
            for plan in plans:
                plan_text = f"{plan[0]} | {plan[1]} | {plan[2]} | KES {plan[3]}"
                combo.addItem(plan_text)
            conn.close()
        except Exception as e:
            print("Failed to load membership plans:", e)
