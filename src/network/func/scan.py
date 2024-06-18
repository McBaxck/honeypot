import multiprocessing
import time
from typing import Optional
import netifaces
import threading
import ipaddress
import nmap
from docker.models.networks import Network
from scapy.layers.l2 import ARP, Ether
from scapy.all import srp
from src.network.objects.device import CDevice


class NetworkInterfaces:
    def __init__(self, inets: list[str]) -> None:
        self.content: list[str] = inets

    def __str__(self) -> str:
        buffer: str = "\n--------------------------------------------"
        if self.content:
            buffer += "\nInterface Address4:\n ------------------------------ \n"
            for inet in self.content:
                buffer += f"--> {inet}\n"
        return buffer


class NetworkScanner:
    def __init__(self, networks=Optional[NetworkInterfaces]) -> None:
        self._networks: NetworkInterfaces = get_interfaces_addresses()
        print(self._networks)
        self._buffer_addrs: dict[str, list[CDevice]] = {}
        self._init_buffer_ip_addresses_()

    @property
    def networks(self) -> list[str]:
        return self._networks.content

    @networks.setter
    def networks(self, inets: list[str]) -> None:
        self._networks.content = inets

    def _init_buffer_ip_addresses_(self) -> None:
        self._buffer_addrs: dict[str, list[CDevice]] = {net: [] for net in self._networks.content}

    def arp_scan(self, network):
        """
        Effectue un scan ARP rapide pour détecter les équipements actifs sur un réseau local.

        Args:
            network (str): Plage d'adresses IP à scanner, au format CIDR (par exemple, "192.168.1.0/16").

        Returns:
            list: Liste de tuples (adresse IP, adresse MAC) des équipements détectés.
        """
        print("\t[...] ARP Fast Scanning network {}...".format(network))
        manager = multiprocessing.Manager()
        devices = manager.list()

        # Création du paquet ARP
        arp = ARP(pdst=network)
        # Création du paquet Ethernet
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        # Combinaison des paquets ARP et Ethernet
        packet = ether / arp

        # Utilisation de processus pour paralléliser l'envoi des paquets
        processes = []
        num_processes = 20  # Nombre de processus, ajustable en fonction de la machine
        for _ in range(num_processes):
            process = multiprocessing.Process(target=self.send_receive_arp, args=(packet, devices))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        # Initialiser le buffer si ce n'est pas déjà fait
        if network not in self._buffer_addrs:
            self._buffer_addrs[network] = []

        # Ajout des adresses détectées au buffer
        for device in devices:
            cdevice = CDevice(**device)
            if cdevice not in self._buffer_addrs[network]:
                self._buffer_addrs[network].append(cdevice)

        print("\t[OK] Finished ARP scan: {}".format(network))

    def send_receive_arp(self, packet, devices_list):
        result = srp(packet, timeout=0.2, verbose=0)[0]
        for sent, received in result:
            device = {'ip': received.psrc, 'datas': received.hwsrc}
            if device not in devices_list:
                devices_list.append(device)


    def scan_network(self, network) -> None:
        print("\t[...] Scanning network {}...".format(network))
        res: list[CDevice] = []
        scanner: nmap.PortScanner = nmap.PortScanner()
        result: dict = scanner.scan(hosts=network)
        try:
            for host in result:
                if len(result[host]['ports']) > 0:
                    res.append(CDevice(**dict({'ip': host, 'datas': result[host]})))
        except (OSError, KeyError, IndexError) as _err_pattern_device:
            pass
        for device in res:
            if device not in self._buffer_addrs[network]:
                self._buffer_addrs[network].append(device)
        self._buffer_addrs[network] = res
        print("\t[OK] Finished scan: {}".format(network))

    def start(self, network=None) -> dict[str, list[CDevice]]:
        devices: dict[str, list[Optional[CDevice]]] = {}
        # print("Scanning networks {}...".format(','.join(self._networks.content)))
        for network in self._networks.content:
            _scan_thread: threading.Thread = threading.Thread(target=self.arp_scan, args=(network,))
            _scan_thread.start()
            _scan_thread.join()
        for network, devices in self._buffer_addrs.items():
            print("\nNETWORK: {}\n -------------------------------------".format(network))
            for device in devices:
                print("--> \t[ - ] DEVICE: {}".format(device.ip))
        return devices


def filter_local_ips(ip_cidr_list):
    """
    Filtre les adresses IP locales et de boucle locale d'une liste d'adresses IP CIDR.
    Args:
        ip_cidr_list (list): Liste d'adresses IP CIDR.
    Returns:
        list: Liste d'adresses IP CIDR sans les adresses locales et de boucle locale.
    """
    filtered_ips = []
    # Parcours de la liste d'adresses IP CIDR
    for ip_cidr in ip_cidr_list:
        # Conversion de l'adresse CIDR en objet ipaddress.IPv4Network
        network = ipaddress.IPv4Network(ip_cidr)
        # Vérification si le réseau correspond à une adresse locale ou de boucle locale
        if network.is_loopback:
            print("Ignore loop IP {}".format(ip_cidr))
            continue  # Ignorer les adresses locales et de boucle locale
        else:
            filtered_ips.append(ip_cidr)  # Ajouter l'adresse IP CIDR à la liste filtrée
    return filtered_ips


def get_active_interfaces() -> list[str]:
    # Recherche de l'interface avec une adresse IPv4 (AF_INET)
    res = []
    for inet in netifaces.interfaces():
        addresses = netifaces.ifaddresses(inet)
        if netifaces.AF_INET in addresses:
            res.append(inet)
    return res


def get_interfaces_addresses():
    wifi_interfaces = get_active_interfaces()
    res = []
    for wifi_interface in wifi_interfaces:
        try:
            ip_address = netifaces.ifaddresses(wifi_interface)[netifaces.AF_INET][0]['addr']
            network_prefix = netifaces.ifaddresses(wifi_interface)[netifaces.AF_INET][0]['netmask'].split('.')
            network_ip_address = '.'.join(
                [str(int(bytes_ip_addr) & int(network_bytes_prefix)) for bytes_ip_addr, network_bytes_prefix in
                 zip(ip_address.split('.'), network_prefix)])
            cidr = sum(bin(int(octet)).count('1') for octet in network_prefix)
            res.append(f"{network_ip_address}/{cidr}")
        except KeyError as _e:
            print(_e)
    return NetworkInterfaces(filter_local_ips(res))


if __name__ == '__main__':
    print(get_interfaces_addresses().content)
    network = NetworkScanner()
    network.scan_network()


