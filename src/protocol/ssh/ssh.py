import os
import select
import time
import paramiko
import threading
import socket
import logging

from src.config import DEFAULT_HONEYPOT_USERNAME, DEFAULT_HONEYPOT_PASSWORD
from src.db.postgres import SSHServerCommandHandler
from src.host.devices.linux.registry import Ubuntu

DEFAULT_CWD: str = os.getcwd()

DEFAULT_USER: str = 'sshuser'
DEFAULT_PWD: str = 'password'

# Bannière SSH réaliste (calquée sur le vrai OpenSSH du conteneur Ubuntu-link-hp en
# coulisses) au lieu de la bannière par défaut de paramiko, qui dénonce immédiatement
# un honeypot Python aux scanners qui fingerprint par grab de bannière.
FAKE_SSH_BANNER: str = "SSH-2.0-OpenSSH_10.2p1 Ubuntu-2ubuntu3.2"

# Reachability du conteneur Docker frère "Ubuntu" : en exécution directe sur l'hôte,
# 0.0.0.0 fonctionne. Une fois le honeypot lui-même dockerisé, le conteneur Ubuntu est
# un conteneur frère sur l'hôte Docker, pas joignable via la boucle locale du conteneur
# honeypot — d'où DOCKER_HOST_GATEWAY (mis à host.docker.internal par docker-compose.yml).
DOCKER_HOST_GATEWAY: str = os.environ.get('DOCKER_HOST_GATEWAY', '0.0.0.0')


ssh_logger = logging.getLogger('SSH')


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if ((username == DEFAULT_HONEYPOT_USERNAME) and
                (password == DEFAULT_HONEYPOT_PASSWORD)):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True


class FakeSSHServer:
    def __init__(self, host_key: str, gate) -> None:
        self.host_key = paramiko.RSAKey(filename=host_key)
        self.device: Ubuntu = Ubuntu()
        self.cmd_history: list[str] = []
        self._db: SSHServerCommandHandler = SSHServerCommandHandler()
        self.gate = gate
        self._host: str = ''
        self._port: int = 0
        ssh_logger.info("Initializing SSH...")

    def handle_client(self, client, addr):
        transport = None
        docker_transport = None
        channel = None
        docker_channel = None
        try:
            # Configuration du serveur SSH pour le client
            transport = paramiko.Transport(client)
            transport.local_version = FAKE_SSH_BANNER
            transport.add_server_key(self.host_key)
            server = Server()  # Assurez-vous que Server est correctement défini
            transport.start_server(server=server)
            channel = transport.accept(20)
            ssh_logger.info("Channel accepted from {}".format(client))

            # Detect if channel is already close
            if channel is None:
                raise Exception("Client SSH n'a pas ouvert de canal.")

            # Connexion au conteneur Docker
            docker_transport = paramiko.Transport((DOCKER_HOST_GATEWAY, 2222))
            docker_transport.connect(username=DEFAULT_USER, password=DEFAULT_PWD)
            docker_channel = docker_transport.open_session()
            docker_channel.get_pty()
            docker_channel.invoke_shell()

            # Client buffer to handle commands
            client_buffer: str = ""

            while True:
                # Attendre les données disponibles sur les deux canaux (appel bloquant :
                # avec un timeout de 0.0 cette boucle tournerait en busy-wait à 100% CPU
                # par connexion, ce qui devient vite un problème avec plusieurs clients
                # concurrents).
                readable, _, _ = select.select([channel, docker_channel], [], [])
                for read_channel in readable:
                    if read_channel is channel:
                        # Transmettre les données du client au Docker
                        data = channel.recv(1024)
                        try:
                            client_buffer += data.decode()
                        except UnicodeDecodeError:
                            client_buffer += str(data)
                        if ('\r' in client_buffer) or ('\n' in client_buffer) or ('\r\n' in client_buffer):
                            print("Detect command -> ", client_buffer)
                            log: dict = {
                                'source_ip': addr[0],
                                'source_port': addr[1],
                                'dest_ip': self._host,
                                'dest_port': self._port,
                                'command': client_buffer
                            }
                            ssh_logger.info("Received command: \n" + str(log))

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
            # Close bidirectional channels... (un échec précoce du handshake SSH peut
            # laisser channel/docker_channel/docker_transport non assignés)
            if docker_channel is not None:
                docker_channel.close()
            if docker_transport is not None:
                docker_transport.close()
            if channel is not None:
                channel.close()
            if transport is not None:
                transport.close()

    def start_server(self, host: str, port: int) -> None:
        """"""
        self._host = host
        self._port = port
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(100)
        print(f'Starting SSH Server on {host}:{port}...')
        try:
            while True:
                client, addr = server.accept()
                print('Connection from:', addr)
                if not self.gate.intake(addr[0], addr[1], host, port, 'ssh'):
                    client.close()
                    continue
                threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()
        except KeyboardInterrupt:
            self.device.power_off()
            time.sleep(1)
        finally:
            server.close()
