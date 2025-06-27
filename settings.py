from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QStackedWidget, QSizePolicy, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import hashlib
import pymysql
from style import shared_stylesheet

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(shared_stylesheet)

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Sidebar buttons
        sidebar = QVBoxLayout()
        self.buttons = []

        sections = ["Account", "Appearance", "System", "Notifications", "About"]
        for i, name in enumerate(sections):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, index=i: self.switch_page(index))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.buttons.append(btn)
            sidebar.addWidget(btn)

        sidebar.addStretch()

        # Stacked content
        self.stack = QStackedWidget()
        self.stack.addWidget(self.account_settings())
        self.stack.addWidget(self.appearance_settings())
        self.stack.addWidget(self.system_settings())
        self.stack.addWidget(self.notifications_settings())
        self.stack.addWidget(self.about_section())

        # Default selection
        self.buttons[0].setChecked(True)

        main_layout.addLayout(sidebar, 1)
        main_layout.addWidget(self.stack, 4)

    def switch_page(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.stack.setCurrentIndex(index)

    def account_settings(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Current Username"))
        self.username_display = QLineEdit()
        self.username_display.setReadOnly(True)
        layout.addWidget(self.username_display)

        layout.addWidget(QLabel("Old Password"))
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_password)

        layout.addWidget(QLabel("New Password"))
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password)

        layout.addWidget(QLabel("Confirm New Password"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password)

        update_btn = QPushButton("Update Password")
        update_btn.clicked.connect(self.update_password)
        layout.addWidget(update_btn)

        layout.addStretch()
        return widget

    def appearance_settings(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Toggle Dark/Light Mode (Coming Soon)"))
        layout.addStretch()
        return widget

    def system_settings(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Backup/Restore Database"))
        layout.addStretch()
        return widget

    def notifications_settings(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Enable/Disable Email Reminders"))
        layout.addStretch()
        return widget

    def about_section(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Library System v1.0"))
        layout.addWidget(QLabel("Developed by Coddy"))
        layout.addStretch()
        return widget

    def load_user(self, username, db_conn):
        self.current_user = username
        self.db_conn = db_conn
        self.username_display.setText(username)

    def update_password(self):
        old_pass = self.old_password.text()
        new_pass = self.new_password.text()
        confirm_pass = self.confirm_password.text()

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Error", "New passwords do not match.")
            return

        if len(new_pass) < 8 or not any(c.isupper() for c in new_pass) or not any(c.islower() for c in new_pass) or not any(c in "!@#$%^&*()_+" for c in new_pass):
            QMessageBox.warning(self, "Error", "New password is too weak.")
            return

        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = %s", (self.current_user,))
            result = cursor.fetchone()
            if result is None:
                QMessageBox.critical(self, "Error", "User not found.")
                return

            db_password = result[0]
            if old_pass != db_password:
                QMessageBox.warning(self, "Error", "Old password is incorrect.")
                return

            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_pass, self.current_user))
            self.db_conn.commit()
            QMessageBox.information(self, "Success", "Password updated successfully.")
            self.old_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))