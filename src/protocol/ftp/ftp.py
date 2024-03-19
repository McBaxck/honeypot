from uuid import UUID, uuid4

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from dataclasses import dataclass
import logging


@dataclass
class FTPUser:
    username: str
    password: str
    home: str
    permissions: str
    id: UUID = uuid4()

    def infos(self) -> tuple:
        return self.username, self.password, self.home, self.permissions


DEFAULT_FTP_USER: FTPUser = FTPUser(username="user", password="12345", home=".", permissions="elradfmw")
ftp_logger = logging.getLogger('FTP')

class FakeFTPServer:
    def __init__(self, port=21):
        self.port = port
        self.users: list = [DEFAULT_FTP_USER.infos()]


    def setup_server(self):
        # Configurer la journalisation


        # Créer et configurer l'authorizer
        authorizer = DummyAuthorizer()
        for username, password, homedir, permissions in self.users:
            authorizer.add_user(username, password, homedir, perm=permissions)

        # Configurer l'handler FTP
        handler = FTPHandler
        handler.authorizer = authorizer

        # Créer le serveur FTP
        self.server = FTPServer(("0.0.0.0", self.port), handler)
        ftp_logger.info(f"Serveur FTP démarré sur le port {self.port}")

    def add_user(self, username, password, homedir, perm) -> None:
        self.users.append(FTPUser(username, password, homedir, perm))

    def start_server(self):
        print("Starting FTP Server on port {}...".format(self.port))
        try:
            self.setup_server()
            self.server.serve_forever()
        except Exception as e:
            ftp_logger.error(f"Erreur lors du démarrage du serveur FTP: {e}")

