import socket


def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Параметры подключения
    host = '127.0.0.1'
    port = 12345

    try:
        server_socket.bind((host, port))

        server_socket.listen(1)
        print(f"[*] TCP Сервер слушает на {host}:{port}")

        while True:
            # Принимаем подключение от клиента
            client_socket, client_address = server_socket.accept()
            print(f"[+] Принято подключение от {client_address}")

            try:
                # Получаем данные от клиента
                data = client_socket.recv(1024).decode()
                print(f"[*] Получено: {data}")

                # Отправляем эхо-ответ
                client_socket.send(data.encode())
                print("[*] Отправлен эхо-ответ")

            except Exception as e:
                print(f"[!] Ошибка при обработке клиента: {e}")
            finally:
                # Закрываем соединение с клиентом
                client_socket.close()

    except Exception as e:
        print(f"[!] Ошибка сервера: {e}")
    finally:
        # Закрываем серверный сокет
        server_socket.close()


if __name__ == "__main__":
    start_tcp_server()
