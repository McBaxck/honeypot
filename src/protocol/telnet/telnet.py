import socket
import logging
import threading


class FakeTelnetServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Serveur Telnet démarré sur {self.host}:{self.port}")
        logging.basicConfig(level=logging.INFO, filename='src/protocol/telnet/logs/telnet_server.log', filemode='a+',
                            format='%(asctime)s - %(levelname)s - %(message)s')

    @staticmethod
    def listen_to_client(client, address):
        print(f"Connexion de {address}")
        client.sendall(b"Bienvenue sur le serveur Telnet!\n")
        while True:
            data = client.recv(1024)
            if not data:
                break
            client.sendall(data)
        client.close()

    def start(self):
        while True:
            client, address = self.socket.accept()
            client_thread = threading.Thread(target=self.listen_to_client, args=(client, address))
            client_thread.start()


if __name__ == '__main__':
    server = FakeTelnetServer('0.0.0.0', 23)
    server.start()
