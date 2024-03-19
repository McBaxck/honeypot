import smtplib
from email.mime.text import MIMEText

def send_email(smtp_server, port, sender, recipient, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP(smtp_server, port) as server:
        server.sendmail(sender, [recipient], msg.as_string())
        print("E-mail envoyé avec succès.")

# Paramètres du serveur SMTP
smtp_server = '127.0.0.1'  # Remplacez par l'adresse IP de votre serveur SMTP
port = 1025  # Le port utilisé par votre serveur SMTP

# Détails de l'e-mail
sender = 'exemple@domaine.com'
recipient = 'destinataire@domaine.com'
subject = 'Test du Serveur SMTP'
body = 'Ceci est un message de test envoyé depuis le serveur SMTP.'

send_email(smtp_server, port, sender, recipient, subject, body)
