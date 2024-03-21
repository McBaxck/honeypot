import asyncio

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message
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


def start_smtp(port):
    # Créer une nouvelle boucle d'événements pour le thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    controller = Controller(CustomHandler(), hostname='localhost', port=port)
    controller.start()
    smtp_logger.info(f"Le serveur SMTP est en cours d'exécution sur le port {port}. Utilisez Ctrl+C pour arrêter.")
    try:
        loop.run_forever()
    finally:
        controller.stop()
        loop.close()
