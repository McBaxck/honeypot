import os
import select
import time

import paramiko
import threading
import socket

from src.host.devices.linux.registry import Ubuntu

DEFAULT_SSH_USERNAME: str = "root"
DEFAULT_SSH_PASSWORD: str = "p@ssw0rd"
DEFAULT_CWD: str = os.getcwd()


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

    def handle_client(self, client):
        try:
            # Configuration du serveur SSH pour le client
            transport = paramiko.Transport(client)
            transport.add_server_key(self.host_key)
            server = Server()  # Assurez-vous que Server est correctement défini
            transport.start_server(server=server)
            channel = transport.accept(20)

            if channel is None:
                raise Exception("Client SSH n'a pas ouvert de canal.")

            # Connexion au conteneur Docker
            docker_transport = paramiko.Transport(('0.0.0.0', 2222))
            docker_transport.connect(username='sshuser', password='password')
            docker_channel = docker_transport.open_session()
            docker_channel.get_pty()
            docker_channel.invoke_shell()

            while True:
                # Attendre les données disponibles sur les deux canaux
                readable, _, _ = select.select([channel, docker_channel], [], [], 0.0)

                for read_channel in readable:
                    if read_channel is channel:
                        # Transmettre les données du client au Docker
                        data = channel.recv(1024)
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
            # Fermeture des connexions SSH
            channel.close()
            docker_channel.close()
            docker_transport.close()
            transport.close()

    def fake_shell(self, channel: paramiko.Channel):
        command_buffer: str = ""
        # channel.send(bytes(f"\rjohn@server $> ", 'utf-8'))
        if channel.closed:
            print('Channel is closed.')
        try:
            command = channel.recv(4096).decode('utf-8')
            command_buffer += command
            if "\x7f" in command:
                command_buffer = command_buffer[:-1]
                # channel.send(bytes(f"\rjohn@server $> {command_buffer}", 'utf-8'))
            if "\x03" in command_buffer:
                # channel.send(bytes(f"\r\njohn@server $> ", 'utf-8'))
                command_buffer = ""
            elif "\x1a" in command_buffer:
                # channel.send(bytes(f"\r\njohn@server $> ", 'utf-8'))
                command_buffer = ""
            elif "\x04" in command_buffer:
                # channel.send(bytes(f"\r\njohn@server $> ", 'utf-8'))
                command_buffer = ""
            if ('\n' in command_buffer) or ('\r\n' in command_buffer) or ('\r' in command_buffer):
                command, _, command_buffer = command_buffer.partition('\n')
                encoded_command: bytes = command.strip().encode('utf-8')
                print("executing command on thread-> ", encoded_command)
                # threading.Thread(target=self.device.exec, args=(command, channel)).start()
                channel.send(encoded_command)
                self.cmd_history.append(command_buffer)
                # channel.send(bytes(f"\r\njohn@server $> ", 'utf-8'))
        except socket.timeout:
            pass
        except Exception as e:
            print(f'Error: {e}')

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
