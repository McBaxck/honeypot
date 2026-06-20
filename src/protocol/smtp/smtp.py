import asyncio

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message
from aiosmtpd.smtp import SMTP
from email.message import EmailMessage
import logging

smtp_logger = logging.getLogger('SMTP')


class CustomHandler:
    async def handle_DATA(self, server, session, envelope):
        mail_from = envelope.mail_from
        rcpt_tos = envelope.rcpt_tos
        data = envelope.content  # Données brutes du message
        # print(f"From: {mail_from}")
        # print(f"To: {rcpt_tos}")
        smtp_logger.info(f"Message: {data.decode('utf8', errors='replace')}")
        return '250 Message accepted for delivery'


class GatedSMTP(SMTP):
    """SMTP protocol asyncio qui passe par le ConnectionGate dès l'établissement de la
    connexion, avant tout échange SMTP (HELO/EHLO inclus)."""
    gate = None
    listen_port = None

    def connection_made(self, transport):
        peer = transport.get_extra_info('peername')
        denied = (peer and self.gate is not None
                  and not self.gate.intake(peer[0], peer[1], '0.0.0.0', self.listen_port, 'smtp'))
        # On laisse aiosmtpd initialiser tout son état interne normalement (session,
        # timeout handle, etc. — invariants vérifiés par connection_lost), puis on annule
        # la tâche du handler avant qu'elle ne tourne, pour qu'aucun banner ne soit envoyé.
        super().connection_made(transport)
        if denied:
            if self._handler_coroutine is not None:
                self._handler_coroutine.cancel()
            transport.close()


class GatedController(Controller):
    def __init__(self, handler, gate, port, **kwargs):
        self.gate = gate
        self._listen_port = port
        super().__init__(handler, port=port, **kwargs)

    def factory(self):
        smtp = GatedSMTP(self.handler, **self.SMTP_kwargs)
        smtp.gate = self.gate
        smtp.listen_port = self._listen_port
        return smtp


def start_smtp(host, port, gate):
    # Créer une nouvelle boucle d'événements pour le thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    controller = GatedController(CustomHandler(), gate, port, hostname=host)
    controller.start()
    smtp_logger.info(f"Le serveur SMTP est en cours d'exécution sur le port {port}. Utilisez Ctrl+C pour arrêter.")
    try:
        loop.run_forever()
    finally:
        controller.stop()
        loop.close()
