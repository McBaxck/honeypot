import os
from uuid import UUID, uuid4

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from dataclasses import dataclass, field
import logging

from src.db.postgres import FTPServerLogHandler

# Répertoire leurre servi aux attaquants : jamais le vrai répertoire de travail du
# honeypot (qui serait exposé en lecture/écriture/suppression avec les permissions
# "elradfmw" ci-dessous sinon).
JAIL_DIR: str = os.path.join(os.path.dirname(__file__), 'jail')

# Le mode passif négocie un port aléatoire à chaque transfert : sans plage fixe, rien
# n'est publié par docker-compose et la connexion de données échoue systématiquement.
# masquerade_address est nécessaire en plus : sans elle, pyftpdlib annoncerait l'IP
# interne du conteneur (ex: 172.x.x.x), injoignable depuis l'extérieur de Docker.
FTP_PASSIVE_PORTS_START: int = int(os.environ.get('FTP_PASSIVE_PORTS_START', 60000))
FTP_PASSIVE_PORTS_END: int = int(os.environ.get('FTP_PASSIVE_PORTS_END', 60010))
FTP_MASQUERADE_ADDRESS: str = os.environ.get('FTP_MASQUERADE_ADDRESS')


@dataclass
class FTPUser:
    username: str
    password: str
    home: str
    permissions: str
    id: UUID = field(default_factory=uuid4)

    def infos(self) -> tuple:
        return self.username, self.password, self.home, self.permissions


DEFAULT_FTP_USER: FTPUser = FTPUser(username="user", password="12345", home=JAIL_DIR, permissions="elradfmw")
ftp_logger = logging.getLogger('FTP')

FAKE_FTP_BANNER: str = "(vsFTPd 3.0.5)"


class GatedFTPHandler(FTPHandler):
    """FTPHandler qui passe par le ConnectionGate avant d'accepter la connexion,
    en suivant exactement le pattern déjà utilisé par pyftpdlib pour handle_max_cons_per_ip.
    Journalise aussi les tentatives de login et les transferts de fichiers."""
    gate = None
    listen_port = None
    log_db = None

    def on_connect(self):
        allowed = self.gate.intake(self.remote_ip, self.remote_port, '0.0.0.0', self.listen_port, 'ftp')
        if not allowed:
            msg = "421 Too many connections from the same IP address."
            self.respond_w_warning(msg)
            self.close_when_done()

    def _log_event(self, event: str, username: str = None, filename: str = None) -> None:
        self.log_db.add_log({
            'source_ip': self.remote_ip,
            'source_port': self.remote_port,
            'event': event,
            'username': username,
            'filename': filename,
        })

    def on_login(self, username):
        ftp_logger.info("Login successful: %s from %s", username, self.remote_ip)
        self._log_event('login', username=username)

    def on_login_failed(self, username, password):
        ftp_logger.info("Login failed: %s from %s", username, self.remote_ip)
        self._log_event('login_failed', username=username)

    def on_file_sent(self, file):
        self._log_event('file_sent', filename=file)

    def on_file_received(self, file):
        self._log_event('file_received', filename=file)

    def on_incomplete_file_received(self, file):
        self._log_event('incomplete_file_received', filename=file)


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
        handler.log_db = FTPServerLogHandler()
        handler.banner = FAKE_FTP_BANNER
        handler.passive_ports = range(FTP_PASSIVE_PORTS_START, FTP_PASSIVE_PORTS_END + 1)
        if FTP_MASQUERADE_ADDRESS:
            handler.masquerade_address = FTP_MASQUERADE_ADDRESS

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

