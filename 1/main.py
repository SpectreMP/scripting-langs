import json
import requests
from typing import Dict, Optional


class Client:
    def __init__(self) -> None:
        self.base_url = 'https://jsonplaceholder.typicode.com'
        self.timeout = 30

    def get_even_user_posts(self) -> None:
        try:
            response = requests.get(
                f'{self.base_url}/posts',
                timeout=self.timeout
            )
            response.raise_for_status()
            posts = response.json()

            even_user_posts = [
                post for post in posts
                if post['id'] % 2 == 0
            ][:20]

            print('\nПосты пользователей с четными ID:')
            print(json.dumps(even_user_posts, indent=2, ensure_ascii=False))

        except requests.RequestException as error:
            print(f'Ошибка при получении постов: {error}')

    def create_post(self) -> Optional[Dict]:
        post_data = {
            'title': 'Тестовый пост',
            'body': 'Содержание тестового поста для лабораторной работы',
            'userId': 1
        }

        try:
            response = requests.post(
                f'{self.base_url}/posts',
                json=post_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            created_post = response.json()

            print('\nСозданный пост:')
            print(json.dumps(created_post, indent=2, ensure_ascii=False))

            return created_post

        except requests.RequestException as error:
            print(f'Ошибка при создании поста: {error}')
            return None

    def update_post(self, post_id: int) -> None:
        update_data = {
            'id': post_id,
            'title': 'Обновлённый пост',
            'body': 'Обновленное содержание поста',
            'userId': 1
        }

        try:
            response = requests.put(
                f'{self.base_url}/posts/{post_id}',
                json=update_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            updated_post = response.json()

            print('\nОбновленный пост:')
            print(json.dumps(updated_post, indent=2, ensure_ascii=False))

        except requests.RequestException as error:
            print(f'Ошибка при обновлении поста: {error}')


def main() -> None:
    client = Client()

    client.get_even_user_posts()

    created_post = client.create_post()

    if created_post:
        client.update_post(40)


if __name__ == '__main__':
    main()
