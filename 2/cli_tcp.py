import socket


def start_tcp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '127.0.0.1'
    port = 12345

    try:
        client_socket.connect((host, port))
        print(f"[*] Подключено к серверу {host}:{port}")

        message = "Привет, TCP Сервер!"
        client_socket.send(message.encode())
        print(f"[*] Отправлено: {message}")

        response = client_socket.recv(1024).decode()
        print(f"[*] Получено: {response}")

    except Exception as e:
        print(f"[!] Ошибка клиента: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    start_tcp_client()
