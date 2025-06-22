from PyQt5.QtWidgets import QMessageBox
import mysql.connector

def get_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='library_db'
        )
    except mysql.connector.Error as err:
        QMessageBox.critical(None, "Database Connection Error",
                             f"Failed to connect to the database:\n{err}")
        return None
