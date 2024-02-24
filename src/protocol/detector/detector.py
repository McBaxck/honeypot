import json
from typing import Union, Any

from scapy.layers.dhcp import DHCP
from scapy.layers.dns import DNS
from scapy.layers.inet import IP, TCP, UDP, ICMP


class ProtocolDetector:
    def __init__(self) -> None:
        self.ports: Any = None
        self._load_ports_registry()

    def _load_ports_registry(self) -> None:
        try:
            with open("src/protocol/detector/ports.json", "r") as ports_file:
                self.ports = json.load(ports_file)
        except FileNotFoundError:
            print("ProtocolDetectorError> No ports.json file")
        except json.decoder.JSONDecodeError:
            print("ProtocolDetectorError> wrong format for ports.json file")
        except TypeError:
            print("ProtocolDetectorError> wrong type for ports.json file")

    def auto_detect(self, port: int, cypher: bytes) -> str:
        detect_proto_res: Union[str, None] = self.detect_by_port(port)
        if detect_proto_res is None:
            detect_proto_res = self.detect_by_data(cypher)
            if detect_proto_res is None:
                return '???'
        return detect_proto_res

    def detect_by_port(self, port: int) -> Union[str, None]:
        if self.ports is not None:
            if str(port) in list(self.ports['ports'].keys()):
                return self.ports['ports'][str(port)]
            else:
                return
        else:
            return

    @staticmethod
    def detect_by_data(cypher: bytes):
        try:
            packet = IP(cypher)
            if packet.haslayer(TCP):
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    return "HTTP"
                elif packet[TCP].dport == 443 or packet[TCP].sport == 443:
                    return "HTTPS"
            if packet.haslayer(UDP):
                if packet[UDP].dport == 53 or packet[UDP].sport == 53:
                    return "DNS"
            if packet.haslayer(TCP) and (packet[TCP].dport == 22 or packet[TCP].sport == 22):
                return "SSH"
            if packet.haslayer(TCP) and (packet[TCP].dport == 23 or packet[TCP].sport == 23):
                return "Telnet"
            if packet.haslayer(TCP) and (packet[TCP].dport == 3389 or packet[TCP].sport == 3389):
                return "RDP"
            if packet.haslayer(UDP) and (packet[UDP].dport == 161 or packet[UDP].sport == 161):
                return "SNMP"
            if packet.haslayer(TCP) and (packet[TCP].dport == 443 or packet[TCP].sport == 443):
                return "HTTPS"
            if packet.haslayer(TCP) and (packet[TCP].dport == 80 or packet[TCP].sport == 80):
                return "HTTP"
            if packet.haslayer(ICMP):
                return "ICMP"
            if packet.haslayer(DHCP):
                return "DHCP"
            if packet.haslayer(DNS):
                return "DNS"
            return "Unknown"
            # Ajouter ici d'autres détections pour d'autres protocoles
        except Exception as e:
            print(f"Erreur lors de l'analyse du paquet: {e}")
            return "??"


if __name__ == "__main__":
    p = ProtocolDetector()
    print(p.auto_detect(port=22, cypher=b'HTTP/1.1 200'))
