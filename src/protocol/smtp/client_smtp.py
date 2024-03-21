import smtplib

# Définissez l'adresse IP du serveur SMTP et le port
smtp_server_ip = "127.0.0.1"
smtp_port = 9924

# Créez une connexion SMTP
server = smtplib.SMTP(smtp_server_ip, smtp_port)

# Spécifiez l'expéditeur et le destinataire
from_addr = "expediteur@example.com"
to_addr = "destinataire@example.com"

# Créez votre message
msg = """\
Subject: Test SMTP
From: {}
To: {}

Ceci est un test d'envoi SMTP.""".format(from_addr, to_addr)

# Envoyez l'email
server.sendmail(from_addr, to_addr, msg)

# Fermez la connexion
server.quit()
