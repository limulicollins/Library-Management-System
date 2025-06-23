import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QVBoxLayout, QApplication, QMessageBox, QStyle
)
from PyQt5.QtGui import QPixmap, QFont, QCursor, QIcon
from PyQt5.QtCore import Qt
from db_config import get_connection
from dashboard import Dashboard
from style import shared_stylesheet


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db_connection = get_connection()
        self.setStyleSheet(shared_stylesheet)
        self.setWindowTitle("📚 Coddy Library Management System 📚")
        self.resize(1200, 800)
        self.minimumSize = (1000, 700)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        title = QLabel("Welcome to Coddy Library")
        title.setObjectName("titleLabel")
        forgot_label = QLabel('<a href="#">Forgot Password?</a>')
        forgot_label.setObjectName("forgotLabel")

        self.setStyleSheet("""
            QWidget {
                background-color: #0a0f2c;
                color: #ffffff;
                font-family: 'Orbitron', sans-serif;
            }

            QLineEdit {
                padding: 10px;
                border: 2px solid #00bfff;
                border-radius: 8px;
                background-color: #1c1f3a;
                color: #ffffff;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 2px solid #00ffff;
            }

            QPushButton {
                background-color: #00bfff;
                border: none;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
                color: #0a0f2c;
            }

            QPushButton:hover {
                background-color: #00ffff;
                color: #000;
            }

            QLabel {
                color: #ffffff;
            }

            QLabel#titleLabel {
                font-size: 24px;
                color: #00ffff;
                font-weight: bold;
            }

            QLabel#forgotLabel {
                color: #aaaaaa;
                text-decoration: underline;
            }

            QLabel#forgotLabel:hover {
                color: #00ffff;
            }
        """)

        image_label = QLabel()
        pixmap = QPixmap("assets/images/login.jpg").scaled(500, 600, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setFixedWidth(600)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(40, 60, 40, 40)

        title = QLabel("Welcome to Coddy Library")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # Username with icon
        user_layout = QHBoxLayout()
        user_icon = QLabel()
        user_icon.setPixmap(QPixmap("assets/icons/profile.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        user_icon.setFixedWidth(25)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        user_layout.addWidget(user_icon)
        user_layout.addWidget(self.username_input)

        # Password with icon + eye toggle
        pass_layout = QHBoxLayout()
        lock_icon = QLabel()
        lock_icon.setPixmap(QPixmap("assets/icons/padlock.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lock_icon.setFixedWidth(25)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(QIcon("assets/icons/eyes-closed.png"))
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setStyleSheet("background: transparent; border: none;")
        self.toggle_btn.clicked.connect(self.toggle_password)

        pass_layout.addWidget(lock_icon)
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.toggle_btn)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)

        forgot_label = QLabel('<a href="#">Forgot Password?</a>')
        forgot_label.setAlignment(Qt.AlignRight)
        forgot_label.setOpenExternalLinks(False)
        forgot_label.linkActivated.connect(self.handle_forgot)

        form_layout.addWidget(title)
        form_layout.addSpacing(15)
        form_layout.addLayout(user_layout)
        form_layout.addLayout(pass_layout)
        form_layout.addWidget(login_button)
        form_layout.addWidget(forgot_label)

        main_layout.addWidget(image_label)
        main_layout.addLayout(form_layout)

    def toggle_password(self):
        if self.toggle_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setIcon(QIcon("assets/icons/eyes-closed.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setIcon(QIcon("assets/icons/eyes-opened.png"))

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()

        if result:
            self.dashboard = Dashboard(self.db_connection)
            self.dashboard.show()
            self.close()

        else:
            QMessageBox.warning(self, "Failed", "Invalid username or password")

        conn.close()

    def handle_forgot(self):
        QMessageBox.information(self, "Forgot Password", "Password recovery feature coming soon.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
