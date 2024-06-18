import socket


class OpenPortInet:
    def __init__(self):
        self._ports = {}

    def open_free_port(self, port: int) -> None:
        if port not in self._ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = ('', port)
                sock.bind(server_address)
                sock.listen(1)
                print(f'Listening on port {port}')
                self._ports[port] = sock
                while True:
                    print('Waiting for a connection...')
                    connection, client_address = sock.accept()
                    try:
                        print(f'Connection from {client_address}')
                        while True:
                            data = connection.recv(16)
                            if data:
                                print(f'Received: {data.decode()}')
                            else:
                                break
                    finally:
                        connection.close()
            except Exception as e:
                print(f'Error: {e}')
        else:
            print(f'Port {port} is already in use.')

    def close_port(self, port: int) -> None:
        if port in self._ports:
            try:
                self._ports[port].close()
                del self._ports[port]
                print(f'Port {port} closed.')
            except Exception as e:
                print(f'Error closing port {port}: {e}')
        else:
            print(f'Port {port} is not open.')
