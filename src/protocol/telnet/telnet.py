import socket
import logging
import threading

from src.config import DEFAULT_HONEYPOT_USERNAME, DEFAULT_HONEYPOT_PASSWORD
from src.db.postgres import TelnetServerCommandHandler

telnet_logger = logging.getLogger('TELNET')

MOTD: bytes = b"Ubuntu 22.04.3 LTS\r\n\r\n"
PROMPT: bytes = b"root@ubuntu:~# "

FAKE_PASSWD: bytes = (
    b"root:x:0:0:root:/root:/bin/bash\r\n"
    b"daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\r\n"
    b"bin:x:2:2:bin:/bin:/usr/sbin/nologin\r\n"
    b"sys:x:3:3:sys:/dev:/usr/sbin/nologin\r\n"
    b"ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash\r\n"
)
FAKE_LS: bytes = b"snap  backup.tar.gz  passwords.txt.bak\r\n"
FAKE_UNAME: bytes = b"Linux ubuntu 5.15.0-91-generic #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023 x86_64 GNU/Linux\r\n"
FAKE_PS: bytes = (
    b"  PID TTY          TIME CMD\r\n"
    b"    1 ?        00:00:01 systemd\r\n"
    b"  842 ?        00:00:00 sshd\r\n"
    b" 1337 pts/0    00:00:00 bash\r\n"
    b" 1402 pts/0    00:00:00 ps\r\n"
)
FAKE_IFCONFIG: bytes = (
    b"eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\r\n"
    b"        inet 172.17.0.2  netmask 255.255.0.0  broadcast 172.17.255.255\r\n"
    b"        ether 02:42:ac:11:00:02  txqueuelen 0  (Ethernet)\r\n"
)

# Réponses canées pour les commandes de reconnaissance courantes (style Cowrie) :
# crédible pour un attaquant qui tâte le terrain, sans avoir à exécuter quoi que ce soit.
FAKE_RESPONSES: dict[str, bytes] = {
    'pwd': b"/root\r\n",
    'whoami': b"root\r\n",
    'id': b"uid=0(root) gid=0(root) groups=0(root)\r\n",
    'uname -a': FAKE_UNAME,
    'uname': b"Linux\r\n",
    'ls': FAKE_LS,
    'ls -l': FAKE_LS,
    'ls -la': FAKE_LS,
    'ls -al': FAKE_LS,
    'cat /etc/passwd': FAKE_PASSWD,
    'ps': FAKE_PS,
    'ps aux': FAKE_PS,
    'ifconfig': FAKE_IFCONFIG,
    'ip a': FAKE_IFCONFIG,
    'ip addr': FAKE_IFCONFIG,
}


class FakeTelnetServer:
    def __init__(self, host, port, gate):
        self.host = host
        self.port = port
        self.gate = gate
        self._db: TelnetServerCommandHandler = TelnetServerCommandHandler()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Serveur Telnet démarré sur {self.host}:{self.port}")

    def _read_line(self, client) -> str:
        buffer = b""
        while not buffer.endswith((b"\r\n", b"\n")):
            chunk = client.recv(1)
            if not chunk:
                raise ConnectionError("client closed")
            buffer += chunk
        return buffer.decode(errors='replace').strip()

    def _log_command(self, address, command: str) -> None:
        telnet_logger.info("Received command: %s from %s", command, address)
        self._db.add_log({
            'source_ip': address[0],
            'source_port': address[1],
            'dest_ip': self.host,
            'dest_port': self.port,
            'command': command,
        })

    def listen_to_client(self, client, address):
        print(f"Connexion de {address}")
        try:
            while True:
                client.sendall(MOTD + b"login: ")
                username = self._read_line(client)
                client.sendall(b"Password: ")
                password = self._read_line(client)
                if username == DEFAULT_HONEYPOT_USERNAME and password == DEFAULT_HONEYPOT_PASSWORD:
                    break
                client.sendall(b"\r\nLogin incorrect\r\n\r\n")

            client.sendall(b"\r\nWelcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-91-generic x86_64)\r\n\r\n")
            client.sendall(PROMPT)
            while True:
                command = self._read_line(client)
                if command:
                    self._log_command(address, command)
                if command in ('exit', 'logout', 'quit'):
                    client.sendall(b"logout\r\n")
                    break
                if command:
                    response = FAKE_RESPONSES.get(command)
                    if response is None:
                        response = f"bash: {command.split()[0]}: command not found\r\n".encode()
                    client.sendall(response)
                client.sendall(PROMPT)
        except (ConnectionError, OSError):
            pass
        finally:
            client.close()

    def start(self):
        while True:
            client, address = self.socket.accept()
            if not self.gate.intake(address[0], address[1], self.host, self.port, 'telnet'):
                client.close()
                continue
            client_thread = threading.Thread(target=self.listen_to_client, args=(client, address))
            client_thread.start()
