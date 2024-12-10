import sys
import os
import sqlite3
import requests
import asyncio
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget, QProgressBar, QTextEdit
)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'blog.db')

# Инициализация базы данных


def create_database():
    """Создание базы данных и таблицы posts"""
    conn = None
    try:
        # Проверяем, существует ли база данных
        if os.path.exists(DB_PATH):
            print("База данных уже существует")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                body TEXT
            )
        ''')

        conn.commit()
        print("База данных успешно создана")

    except sqlite3.Error as error:
        print("Ошибка при создании базы данных:", error)
    finally:
        if conn:
            conn.close()

# Класс для управления сигналами


class SignalEmitter(QObject):
    data_loaded = pyqtSignal(list)
    progress_updated = pyqtSignal(int)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Многозадачность в PyQt5")

        self.load_button = QPushButton("Загрузить данные")
        self.progress_bar = QProgressBar()
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(QLabel("Прогресс:"))
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Лог:"))
        layout.addWidget(self.log)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_button.clicked.connect(self.start_loading)

        # Таймер для периодической проверки
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_updates)
        self.timer.start(10000)  # Проверка каждые 10 секунд

        # Инициализация сигнала
        self.signals = SignalEmitter()
        self.signals.data_loaded.connect(self.display_data)
        self.signals.progress_updated.connect(self.update_progress)

    def start_loading(self):
        self.log.append("Начало загрузки данных...")
        thread = threading.Thread(target=self.load_data)
        thread.start()

    def load_data(self):
        try:
            url = "https://jsonplaceholder.typicode.com/posts"
            response = requests.get(url)
            posts = response.json()
            self.signals.progress_updated.emit(50)

            # Сохранение данных асинхронно
            asyncio.run(self.save_data(posts))
        except Exception as e:
            self.log.append(f"Ошибка загрузки: {e}")

    async def save_data(self, posts):
        await asyncio.sleep(2)
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.executemany("""
            INSERT OR REPLACE INTO posts (id, user_id, title, body)
            VALUES (?, ?, ?, ?)
        """, [(post['id'], post['userId'], post['title'], post['body']) for post in posts])
        connection.commit()
        connection.close()

        self.signals.progress_updated.emit(100)
        self.signals.data_loaded.emit(posts)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_data(self, posts):
        self.log.append("Данные успешно сохранены в базе:")
        for post in posts[:5]:  # Показываем первые 5 записей
            self.log.append(f"{post['id']}: {post['title']}")

    def check_updates(self):
        self.log.append("Проверка обновлений...")

        try:
            # Выполняем запрос на сервер
            url = "https://jsonplaceholder.typicode.com/posts"
            response = requests.get(url)
            posts = response.json()

            # Получаем текущие ID постов в базе данных
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM posts")
            existing_post_ids = {post[0] for post in cursor.fetchall()}
            connection.close()

            # Проверяем, появились ли новые посты или обновления
            new_posts = [post for post in posts if post['id']
                         not in existing_post_ids]

            if new_posts:
                self.log.append(f"Обнаружено {len(new_posts)} новых постов!")
                # Сохраняем новые посты в базу
                asyncio.run(self.save_data(new_posts))
            else:
                self.log.append("Нет новых обновлений.")

        except requests.RequestException as error:
            self.log.append(f"Ошибка при проверке обновлений: {error}")


if __name__ == "__main__":
    create_database()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
