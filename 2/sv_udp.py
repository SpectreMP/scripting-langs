import socket


def start_udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Задаем параметры подключения
    host = '127.0.0.1'
    port = 12346

    try:
        # Привязываем сокет к адресу и порту
        server_socket.bind((host, port))
        print(f"[*] UDP Сервер слушает на {host}:{port}")

        while True:
            try:
                # Получаем данные и адрес клиента
                data, client_address = server_socket.recvfrom(1024)
                message = data.decode()
                print(f"[*] Получено от {client_address}: {message}")

                # Отправляем эхо-ответ
                server_socket.sendto(data, client_address)
                print(f"[*] Отправлен эхо-ответ на {client_address}")

            except Exception as e:
                print(f"[!] Ошибка при обработке сообщения: {e}")

    except Exception as e:
        print(f"[!] Ошибка сервера: {e}")
    finally:
        # Закрываем серверный сокет
        server_socket.close()


if __name__ == "__main__":
    start_udp_server()
