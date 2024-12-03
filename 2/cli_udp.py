import socket


def start_udp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    host = '127.0.0.1'
    port = 12346

    try:
        message = "Привет, UDP Сервер!"
        client_socket.sendto(message.encode(), (host, port))
        print(f"[*] Отправлено: {message}")

        data, _ = client_socket.recvfrom(1024)
        response = data.decode()
        print(f"[*] Получено: {response}")

    except Exception as e:
        print(f"[!] Ошибка клиента: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    start_udp_client()
