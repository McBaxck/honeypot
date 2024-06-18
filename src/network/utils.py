import random
import socket
import uuid
import bcrypt
import requests
import netifaces
from scapy.all import srp
from scapy.layers.l2 import ARP, Ether
import logging

logging.getLogger("scapy.runtime").setLevel(logging.INFO)
logging.getLogger("scapy.loading").setLevel(logging.INFO)
logging.getLogger("scapy.interactive").setLevel(logging.INFO)
logging.getLogger("scapy.automaton").setLevel(logging.INFO)


def get_public_ip():
    import time
    time.sleep(random.randint(1, 5))
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json()['ip']
        return ip
    except Exception as e:
        return None


def get_private_ip_and_iface():
    # Cette fonction suppose que vous êtes connecté à internet via la première interface réseau non-locale trouvée
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface != 'lo':
            addr = netifaces.ifaddresses(interface)
            try:
                ip_info = addr[netifaces.AF_INET][0]
                return ip_info['addr'], interface
            except KeyError:
                pass
    return None, None


def get_gateway_ip():
    gws = netifaces.gateways()
    default_gateway = gws['default'][netifaces.AF_INET]
    return default_gateway[0]


def ip_to_binary(ip):
    return ''.join([f'{int(x):08b}' for x in ip.split('.')])


def scan_network(ip_range):
    """
    Scanne le réseau en envoyant des requêtes ARP et affiche les adresses IP, MAC et, si possible, les hostnames des appareils trouvés.

    :param ip_range: La plage d'adresses IP à scanner, sous forme de chaîne, par exemple "192.168.1.1/24".
    """
    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    devices = []
    for sent, received in answered_list:
        hostname = 'Inconnu'
        try:
            # Tente de résoudre l'adresse IP en hostname
            hostname = socket.gethostbyaddr(received.psrc)[0]
        except socket.herror:
            # Ne parvient pas à résoudre l'IP en hostname
            pass
        devices.append({'ip': received.psrc, 'mac': received.hwsrc, 'hostname': hostname})
    return devices


def get_active_interface_details():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface == 'lo':
            continue  # Ignorer l'interface de boucle locale
        try:
            addr_info = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addr_info:
                for ip_info in addr_info[netifaces.AF_INET]:
                    if 'addr' in ip_info and 'netmask' in ip_info:
                        # Vérifier que l'adresse n'est pas de boucle locale
                        if not ip_info['addr'].startswith("127."):
                            return ip_info['addr'], interface, ip_info['netmask']
        except ValueError:
            continue
    return None, None, None


def calculate_network_address(ip, netmask):
    ip_binary = ''.join(f'{int(x):08b}' for x in ip.split('.'))
    netmask_binary = ''.join(f'{int(x):08b}' for x in netmask.split('.'))
    network_binary = ''.join('1' if ip_binary[i] == '1' and netmask_binary[i] == '1' else '0' for i in range(32))
    network_address = '.'.join(str(int(network_binary[i:i + 8], 2)) for i in range(0, 32, 8))
    return network_address


def netmask_to_cidr(netmask):
    return str(bin(int(''.join([f'{int(octet):08b}' for octet in netmask.split('.')]), 2)).count('1'))


def get_network_ip_with_cidr():
    private_ip, interface, netmask = get_active_interface_details()
    if private_ip and netmask:
        network_ip = calculate_network_address(private_ip, netmask)
        cidr = netmask_to_cidr(netmask)
        return f"{network_ip}/{cidr}"
    else:
        return "No active network interface found."


import netifaces as ni


def get_default_gateway():
    return ni.gateways()['default'][ni.AF_INET][0]


def get_own_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        return '127.0.0.1'


def get_own_mac_addr():
    # Obtention de l'adresse MAC en tant qu'entier 48 bits
    mac = uuid.getnode()

    # Conversion de l'adresse MAC en une chaîne de caractères formatée
    mac_address = ':'.join(f'{mac:012x}'[i:i + 2] for i in range(0, 12, 2))
    return mac_address


def get_mac_address(ip_address):
    arp_request = ARP(pdst=ip_address)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered = srp(arp_request_broadcast, timeout=1, verbose=False, iface_hint=ip_address)[0]
    if answered:
        return answered[0][1].hwsrc
    else:
        return "??"


def get_os_version():
    import platform
    os_name = platform.system()  # Obtient le nom du système d'exploitation (ex. Linux, Windows, Darwin)
    os_version = platform.version()  # Obtient la version spécifique du système d'exploitation
    return os_version


def get_memory_info():
    import psutil
    # Mémoire RAM
    ram_info = psutil.virtual_memory()
    total_ram = ram_info.total / (1024 ** 3)  # Convertir en Gigaoctets (Go)
    available_ram = ram_info.available / (1024 ** 3)  # Convertir en Go
    used_ram = ram_info.used / (1024 ** 3)  # Convertir en Go

    # Espace de stockage (Pour le disque où le script est exécuté)
    disk_info = psutil.disk_usage('/')
    total_disk = disk_info.total / (1024 ** 3)  # Convertir en Go
    used_disk = disk_info.used / (1024 ** 3)  # Convertir en Go
    free_disk = disk_info.free / (1024 ** 3)  # Convertir en Go

    return f"{int(total_ram)}Go RAM, {int(total_disk)}Go SSD"


def scan(ip_range):
    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    clients_list = []

    for element in answered_list:
        client_dict = {
            "ip": element[1].psrc,
            "mac": element[1].hwsrc,
            # Les résolutions de hostname et fabricant doivent être implémentées ici.
        }
        clients_list.append(client_dict)
    all_ips: list[str] = [list(el.values())[0] for el in clients_list]
    gtw: str = get_gateway_ip()
    my_ip: str = get_own_ip()
    if gtw not in all_ips:
        clients_list.append({"ip": gtw, "mac": get_mac_address(gtw)})
    if my_ip not in all_ips:
        clients_list.append({"ip": my_ip, "mac": get_own_mac_addr()})
    print("All iPV4 addresses: ", all_ips)
    return clients_list


# Fonction pour hacher un mot de passe
def hash_password(password):
    # Convertir le mot de passe en bytes, générer un sel et hacher le mot de passe
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password


# Fonction pour vérifier un mot de passe contre un hachage
def check_password(hashed_password, user_password):
    # Convertir le mot de passe utilisateur en bytes et vérifier
    user_password_bytes = user_password.encode('utf-8')
    return bcrypt.checkpw(user_password_bytes, hashed_password)


if __name__ == "__main__":
    # Utilisation de la fonction pour scanner le réseau, par exemple 192.168.1.1/24 pour un réseau local typique.
    devices = scan(get_network_ip_with_cidr())
    for device in devices:
        print(device)
