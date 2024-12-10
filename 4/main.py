import os
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableView, QDialog, QFormLayout
)
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'blog.db')


class DatabaseConnection:
    def __init__(self, db_name="blog.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(base_dir, db_name)
        self.connection = None
        self.create_database()

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            return True
        except sqlite3.Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def create_database(self):
        """Создание базы данных и таблицы posts"""
        # Проверяем, существует ли база данных
        if os.path.exists(self.db_name):
            print("База данных уже существует")
            return

        try:
            self.connection = sqlite3.connect(self.db_name)
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    title TEXT,
                    body TEXT
                )
            ''')
            self.connection.commit()
            print("База данных успешно создана")
        except sqlite3.Error as error:
            print("Ошибка при создании базы данных:", error)
        finally:
            if self.connection:
                self.connection.close()


class AddRecordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить запись")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        self.user_id_field = QLineEdit()
        self.title_field = QLineEdit()
        self.body_field = QLineEdit()

        layout.addRow("User ID:", self.user_id_field)
        layout.addRow("Title:", self.title_field)
        layout.addRow("Body:", self.body_field)

        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.cancel_button = QPushButton("Отмена")
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addRow(buttons_layout)

        self.add_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_data(self):
        return {
            "user_id": self.user_id_field.text(),
            "title": self.title_field.text(),
            "body": self.body_field.text()
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Просмотр базы данных")
        self.db = DatabaseConnection(DB_PATH)
        if not self.db.connect():
            print("Не удалось подключиться к базе данных")
            sys.exit(1)

        self.setup_ui()
        self.setup_database()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск по заголовку...")
        self.search_field.textChanged.connect(self.search_posts)
        layout.addWidget(self.search_field)

        self.table_view = QTableView()
        layout.addWidget(self.table_view)

        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Обновить")
        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")
        self.refresh_button.clicked.connect(self.refresh_data)
        self.add_button.clicked.connect(self.add_record)
        self.delete_button.clicked.connect(self.delete_record)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

    def setup_database(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(self.db.db_name)

        if not db.open():
            print("Не удалось открыть базу данных.")
            return

        self.db_model = QSqlTableModel()
        self.db_model.setTable("posts")
        self.db_model.select()
        self.db_model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.db_model.setHeaderData(0, Qt.Horizontal, "ID")
        self.db_model.setHeaderData(1, Qt.Horizontal, "User ID")
        self.db_model.setHeaderData(2, Qt.Horizontal, "Title")
        self.db_model.setHeaderData(3, Qt.Horizontal, "Body")
        self.table_view.setModel(self.db_model)
        self.table_view.setSelectionBehavior(self.table_view.SelectRows)

    def search_posts(self, text):
        self.db_model.setFilter(f"title LIKE '%{text}%'")
        self.db_model.select()

    def refresh_data(self):
        self.db_model.select()

    def add_record(self):
        dialog = AddRecordDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            if data["user_id"] and data["title"] and data["body"]:
                row = self.db_model.rowCount()
                self.db_model.insertRow(row)
                self.db_model.setData(self.db_model.index(
                    row, 1), int(data["user_id"]))
                self.db_model.setData(
                    self.db_model.index(row, 2), data["title"])
                self.db_model.setData(
                    self.db_model.index(row, 3), data["body"])
                if not self.db_model.submitAll():
                    print("Ошибка добавления записи:",
                          self.db_model.lastError().text())
                else:
                    self.refresh_data()

    def delete_record(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            print("Нет выбранных записей для удаления.")
            return
        for index in selected_rows:
            self.db_model.removeRow(index.row())
        if not self.db_model.submitAll():
            print("Ошибка удаления записи:", self.db_model.lastError().text())
        else:
            self.refresh_data()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
