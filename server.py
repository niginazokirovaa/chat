import socket
import select
import datetime

def send_to_all(sock, message):
    for socket in connected_list:
        if socket != server_socket and socket != sock:
            try:
                socket.send(message.encode())
            except:
                socket.close()
                connected_list.remove(socket)

if __name__ == "__main__":
    name = ""
    record = {}
    connected_list = []
    buffer = 4096
    port = 5001

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(10)

    connected_list.append(server_socket)

    server_ip = socket.gethostbyname(socket.gethostname())
    print(f"СЕРВЕР РАБОТАЕТ! IP: {server_ip}, PORT: {port}")

    log_file = open("chat_log.txt", "a")

    try:
        while True:
            rList, _, error_sockets = select.select(connected_list, [], [])
            for sock in rList:
                if sock == server_socket:
                    sockfd, addr = server_socket.accept()
                    name = sockfd.recv(buffer).decode().strip()
                    connected_list.append(sockfd)
                    record[addr] = ""
                    if name in record.values():
                        sockfd.send("Имя пользователя уже занято!\n".encode())
                        del record[addr]
                        connected_list.remove(sockfd)
                        sockfd.close()
                        continue
                    else:
                        record[addr] = name
                        print(f"Клиент ({addr[0]}, {addr[1]}) подключился [{record[addr]}]")
                        sockfd.send("Добро пожаловать в чат. Введите 'exit' для выхода в любое время.\n".encode())
                        send_to_all(sockfd, f"{name} присоединился к беседе.\n")
                else:
                    try:
                        data1 = sock.recv(buffer)
                        i, p = sock.getpeername()
                        data = data1[:data1.index(b"\n")].decode().strip()
                        if data == "exit":
                            msg = f"{record[(i, p)]} покинул беседу.\n"
                            send_to_all(sock, msg)
                            print(f"Клиент ({i}, {p}) отключился [{record[(i, p)]}]")
                            del record[(i, p)]
                            connected_list.remove(sock)
                            sock.close()
                            continue
                        else:
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_msg = f"[{timestamp}] {record[(i, p)]}: {data}"
                            print(log_msg)
                            log_file.write(log_msg + "\n")
                            msg = f"{record[(i, p)]}: {data}\n"
                            send_to_all(sock, msg)
                    except:
                        i, p = sock.getpeername()
                        send_to_all(sock, f"{record[(i, p)]} неожиданно покинул беседу.\n")
                        print(f"Клиент ({i}, {p}) отключился (ошибка) [{record[(i, p)]}]")
                        log_file.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Клиент ({i}, {p}) отключился (ошибка) [{record[(i, p)]}]\n")
                        del record[(i, p)]
                        connected_list.remove(sock)
                        sock.close()
                        continue
    except KeyboardInterrupt:
        print("\nСЕРВЕР ОСТАНОВЛЕН!")
        log_file.close()
        server_socket.close()
