shared_stylesheet = """
QWidget {
    background-color: #0a0f2c;
    color: white;
    font-family: Segoe UI, sans-serif;
    font-size: 14px;
}

QLineEdit, QComboBox, QDateEdit, QTextEdit {
    background-color: #2e2e2e;
    color: white;
    border-radius: 8px;
    padding: 6px;
}

QPushButton {
    background-color: #00FFFF;
    color: black;
    padding: 8px 16px;
    font-weight: bold;
    border: none;
    border-radius: 8px;
}

QPushButton:hover {
    background-color: #00cccc;
}

QPushButton:pressed {
    background-color: #009999;
}

QTableWidget {
    background-color: #2a2a2a;
    color: white;
    border: none;
    border-radius: 8px;
}

QHeaderView::section {
    background-color: #00FFFF;
    color: black;
    font-weight: bold;
}

QGroupBox {
    border: 2px solid #00FFFF;
    border-radius: 8px;
    margin-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #00FFFF;
    font-weight: bold;
}

QLabel {
    color: #ffffff;
    font-size: 16px;
    font-weight: bold;
}

QLabel#titleLabel {
    font-size: 20px;
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

QHBoxLayout {
    color: white; 
    font-size: 24px; 
    font-weight: bold;
}
"""
