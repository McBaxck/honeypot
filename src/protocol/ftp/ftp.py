from uuid import UUID, uuid4

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from dataclasses import dataclass, field
import logging


@dataclass
class FTPUser:
    username: str
    password: str
    home: str
    permissions: str
    id: UUID = field(default_factory=uuid4)

    def infos(self) -> tuple:
        return self.username, self.password, self.home, self.permissions


DEFAULT_FTP_USER: FTPUser = FTPUser(username="user", password="12345", home=".", permissions="elradfmw")
ftp_logger = logging.getLogger('FTP')


class GatedFTPHandler(FTPHandler):
    """FTPHandler qui passe par le ConnectionGate avant d'accepter la connexion,
    en suivant exactement le pattern déjà utilisé par pyftpdlib pour handle_max_cons_per_ip."""
    gate = None
    listen_port = None

    def on_connect(self):
        allowed = self.gate.intake(self.remote_ip, self.remote_port, '0.0.0.0', self.listen_port, 'ftp')
        if not allowed:
            msg = "421 Too many connections from the same IP address."
            self.respond_w_warning(msg)
            self.close_when_done()


class FakeFTPServer:
    def __init__(self, port=21, gate=None):
        self.port = port
        self.gate = gate
        self.users: list = [DEFAULT_FTP_USER.infos()]


    def setup_server(self):
        # Créer et configurer l'authorizer
        authorizer = DummyAuthorizer()
        for username, password, homedir, permissions in self.users:
            authorizer.add_user(username, password, homedir, perm=permissions)

        # Configurer l'handler FTP
        handler = GatedFTPHandler
        handler.authorizer = authorizer
        handler.gate = self.gate
        handler.listen_port = self.port

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
        except Exception:
            ftp_logger.exception("Erreur lors du démarrage du serveur FTP")

