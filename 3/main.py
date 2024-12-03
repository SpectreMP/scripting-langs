import sqlite3
import requests
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'blog.db')


def create_database():
    connection = None

    try:
        if os.path.exists(DB_PATH):
            print("База данных уже существует")
            return

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                body TEXT
            )
        ''')

        connection.commit()
        print("База данных успешно создана")

    except sqlite3.Error as error:
        print("Ошибка при создании базы данных:", error)
    finally:
        if connection:
            connection.close()


def fetch_posts():
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/posts')
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print("Ошибка при получении данных:", error)
        return None


def save_posts(posts):
    if not posts:
        return

    connection = None
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.executemany(
            'INSERT OR REPLACE INTO posts (id, user_id, title, body) VALUES (?, ?, ?, ?)',
            [(post['id'], post['userId'], post['title'], post['body']) for post in posts]
        )

        connection.commit()
        print(f"Успешно сохранено {len(posts)} постов")

    except sqlite3.Error as error:
        print("Ошибка при сохранении данных:", error)
    finally:
        if connection:
            connection.close()


def get_user_posts(user_id):
    connection = None
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM posts WHERE user_id = ?', (user_id,))
        posts = cursor.fetchall()

        return posts

    except sqlite3.Error as error:
        print("Ошибка при получении постов пользователя:", error)
        return []
    finally:
        if connection:
            connection.close()


def main():
    create_database()
    posts = fetch_posts()
    if posts:
        save_posts(posts)

    user_id = int(input("Введите ID запрашиваемого пользователя: "))
    user_posts = get_user_posts(user_id)
    print(f"\nПосты пользователя {user_id}:")
    for post in user_posts:
        print(f"ID: {post[0]}")
        print(f"Заголовок: {post[2]}")
        print(f"Текст: {post[3]}...")
        print("-" * 50)


if __name__ == "__main__":
    main()
