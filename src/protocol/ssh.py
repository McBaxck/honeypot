import os
import paramiko
import threading
import socket
from src.host.system import FHS
from typing import Optional

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'user') and (password == 'password'):
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
        self.fhs: FHS = FHS()


    def handle_client(self, client):
        transport = paramiko.Transport(client)
        transport.add_server_key(self.host_key)
        server = Server()
        transport.start_server(server=server)
        channel = transport.accept(20)
        try:
            fake_shell(channel)
        finally:
            channel.close()

    def handle_command(self, command: str) -> str:
        if command in ['pwd', 'cwd', 'whereami', 'echo $PATH']:
            return self.fhs.pwd()
        if command.startswith('nano') or command.startswith('vim'):
            filename: Optional[str] = command.split(' ')[1]
            return self.fhs.nano(filename)
        if command == 'cd':
            directory: Optional[str] = command.split(' ')[1]
            return self.fhs.cd(directory)
        return 'unknown command'

    def fake_shell(self, channel: paramiko.Channel):
        full_command: list[str] = []
        channel.send("user@server ~ $> ")
        while True:
            if channel.closed:
                print('Channel is closed.')
                break
            try:
                command = channel.recv(1024).decode('utf-8').strip()
                full_command.append(command)
                if command == 'exit':
                    channel.send('Exiting...\n')
                    break
                if '' in full_command:
                    print(os.system(''.join(full_command)))
                    full_command.clear()
                    channel.send("\r\nuser@server ~ $> ")
                channel.send(f'{command}')
            except socket.timeout:
                continue
            except Exception as e:
                print(f'Error: {e}')
                break

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', 2222))
        server.listen(100)

        print('Listening for connection ...')
        while True:
            client, addr = server.accept()
            print('Connection from:', addr)
            threading.Thread(target=handle_client, args=(client,)).start()


if __name__ == '__main__':
    start_server()
