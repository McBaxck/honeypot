import ipaddress

from src.host import nslookup_with_geolocation
from src.protocol.detector.detector import detect_protocol


def _classify_country(ip: str) -> str:
    if ip == 'localhost':
        return 'LOCAL'
    address = ipaddress.IPv4Address(ip)
    if address.is_global:
        return nslookup_with_geolocation(ip)
    if address.is_private:
        return 'LOCAL_POS'
    return '??'


class ConnectionGate:
    """Point d'entrée unique pour toute connexion entrante, quel que soit le protocole :
    vérifie le rate-limit, met à jour l'historique, et journalise dans la table générique
    `logs`, avant que le handler du protocole ne prenne le relais."""

    def __init__(self, firewall, history, db):
        self._firewall = firewall
        self._history = history
        self._db = db

    def intake(self, ip: str, port: int, dest_ip: str, dest_port: int, protocol: str, data: str = '') -> bool:
        """Retourne True si la connexion peut continuer, False si elle doit être rejetée
        immédiatement (rate-limit dépassé)."""
        allowed = self._firewall.add_connection(ip)
        self._history.store(ip)
        self._db.add_log({
            'type': 'tcp',
            'source_ip': ip,
            'source_port': port,
            'data': data,
            'dest_port': dest_port,
            'dest_ip': dest_ip,
            'protocol': protocol if protocol != 'auto' else detect_protocol(data),
            'country': _classify_country(ip),
        })
        return allowed
