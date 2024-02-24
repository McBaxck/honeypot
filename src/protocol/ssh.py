import os
import select
import time
import paramiko
import threading
import socket

from src.db.supabase import SSHServerCommandHandler
from src.host.devices.linux.registry import Ubuntu

DEFAULT_SSH_USERNAME: str = "root"
DEFAULT_SSH_PASSWORD: str = "p@ssw0rd"
DEFAULT_CWD: str = os.getcwd()

DEFAULT_USER: str = 'sshuser'
DEFAULT_PWD: str = 'password'


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if ((username == DEFAULT_SSH_USERNAME) and
                (password == DEFAULT_SSH_PASSWORD)):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True


class FakeSSHServer:
    def __init__(self, host_key: str) -> None:
        self.host_key = paramiko.RSAKey(filename=host_key)
        self.device: Ubuntu = Ubuntu()
        self.cmd_history: list[str] = []
        self._db: SSHServerCommandHandler = SSHServerCommandHandler()

    def handle_client(self, client):
        try:
            # Configuration du serveur SSH pour le client
            transport = paramiko.Transport(client)
            transport.add_server_key(self.host_key)
            server = Server()  # Assurez-vous que Server est correctement défini
            transport.start_server(server=server)
            channel = transport.accept(20)

            # Detect if channel is already close
            if channel is None:
                raise Exception("Client SSH n'a pas ouvert de canal.")

            # Connexion au conteneur Docker
            docker_transport = paramiko.Transport(('0.0.0.0', 2222))
            docker_transport.connect(username=DEFAULT_USER, password=DEFAULT_PWD)
            docker_channel = docker_transport.open_session()
            docker_channel.get_pty()
            docker_channel.invoke_shell()

            # Client buffer to handle commands
            client_buffer: str = ""

            while True:
                # Attendre les données disponibles sur les deux canaux
                readable, _, _ = select.select([channel, docker_channel], [], [], 0.0)
                for read_channel in readable:
                    if read_channel is channel:
                        # Transmettre les données du client au Docker
                        data = channel.recv(1024)
                        client_buffer += data.decode()
                        if ('\r' in client_buffer) or ('\n' in client_buffer) or ('\r\n' in client_buffer):
                            print("Detect command -> ", client_buffer)
                            log: dict = {
                                'source_ip': '',
                                'source_port': 0,
                                'dest_ip': '',
                                'dest_port': 0,
                                'command': client_buffer
                            }
                            self._db.add_log(log)
                            client_buffer = ""
                        if not data:
                            break  # Le client a fermé la connexion
                        docker_channel.send(data)
                    elif read_channel is docker_channel:
                        # Transmettre les données du Docker au client, incluant stdout et stderr
                        data = docker_channel.recv(1024)
                        if not data:
                            break  # Le canal Docker a été fermé
                        channel.send(data)
        except Exception as e:
            print(f"Erreur lors de la transmission du shell: {e}")
        finally:
            # Close bidirectional channels...
            docker_channel.close()
            channel.close()

    def start_server(self, host: str, port: int) -> None:
        """"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(100)
        print(f'Starting SSH Server on {host}:{port}...')
        try:
            while True:
                client, addr = server.accept()
                print('Connection from:', addr)
                # threading.Thread(target=self.handle_client, args=(client,)).start()
                self.handle_client(client)
        except KeyboardInterrupt:
            self.device.power_off()
            time.sleep(1)
