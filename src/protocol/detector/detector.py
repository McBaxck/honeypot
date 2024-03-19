import re
import socket


def detect_protocol(data):
    # Dictionnaire des protocoles avec leurs signatures ou motifs spécifiques
    protocols = {
        "HTTP": [b"GET ", b"POST ", b"PUT ", b"DELETE ", b"CONNECT ", b"OPTIONS ", b"TRACE ", b"PATCH ", b"HTTP/1.",
                 b"HTTP/2."],
        "SSH": [b"SSH-2.0-", b"SSH-1.99-"],
        "DNS": [b"\x00\x01", b"\x01\x00"],  # Exemple simplifié
        "FTP": [b"220 ", b"USER ", b"PASS "],
        "SMTP": [b"220 ", b"EHLO ", b"HELO ", b"MAIL FROM:", b"RCPT TO:"],
        "Telnet": [b"\xff\xfb\x01", b"\xff\xfb\x03"],
        "SNMP": [b"\x30\x2d\x02\x01\x03"],  # Signature simplifiée pour SNMPv3
        "DHCP": [b"\x63\x82\x53\x63"],  # Signature pour les messages DHCP
        "SIP": [b"SIP/2.0"],  # Signature simplifiée pour SIP
        "RTSP": [b"RTSP/1.0"],  # Signature pour RTSP
        "IMAP": [b"* OK IMAP4"],  # Réponse de serveur IMAP simplifiée
        "POP3": [b"+OK POP3"],  # Réponse de serveur POP3
        # Plus de protocoles et leurs signatures peuvent être ajoutés ici
    }

    # Convertir les données en bytes si nécessaire
    if isinstance(data, str):
        data = data.encode('utf-8', errors='ignore')

    # Analyser les données reçues pour chaque protocole
    for protocol, signatures in protocols.items():
        for signature in signatures:
            if data.startswith(signature) or signature in data:
                return protocol

    # Analyse basée sur des caractéristiques plus complexes si nécessaire
    # Exemple: analyse de la structure pour des protocoles moins textuels ou cryptés

    return "Unknown"

