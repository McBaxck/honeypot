import asyncio
import time
import logging
from aiosmtpd.controller import Controller

smtp_logger = logging.getLogger('SMTP')


class FakeSMTPServer:
    async def handle_DATA(self, server, session, envelope):
        peer = session.peer
        mailfrom = envelope.mail_from
        rcpttos = envelope.rcpt_tos
        data = envelope.content.decode('utf8', errors='replace')

        # Afficher et enregistrer le message dans la console et dans le fichier de log
        message = f'Received message from {peer}\nFrom: {mailfrom}\nTo: {rcpttos}\nMessage:\n{data}'
        smtp_logger.info(message)
        # Enregistrer le message dans un fichier
        # with open('received_emails.txt', 'a') as file:
        #     file.write(f'From: {mailfrom}, To: {rcpttos}, Message: {data}\n')

        return '250 Message accepted for delivery'


async def start_smtp_server(port=25):
    handler = FakeSMTPServer()
    controller = Controller(handler, hostname='127.0.0.1', port=port)

    # Lancer le serveur de manière asynchrone
    controller.start()
    try:
        print("SMTP Server started...")
        await asyncio.Future()  # Boucle infinie jusqu'à une interruption
    except (Exception, KeyboardInterrupt):
        print("SMTP Server is stopping...")
        time.sleep(2)
    finally:
        controller.stop()
