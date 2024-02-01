import socket
import time
import random
import ipaddress
from src.host.host import Host


def create_udp_socket(host: str, port: int, timeout=None) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    sock.setblocking(False)
    sock.bind((host, port))
    return sock


def create_tcp_socket(host: str, port: int, timeout=None) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(False)
    sock.bind((host, port))
    sock.listen(100)
    return sock


def handle_tcp_connection(sock: socket.socket) -> tuple[Host, bytes]:
    """"""
    client, address = sock.accept()
    host: Host = Host(name='?',
                      mac='?',
                      ip4=(ipaddress.ip_address(address[0]),),
                      os='?')
    time.sleep(.5 * random.random())
    data = client.recv(2048)
    client.sendall(data)
    print(f"TCP > Received {data} from {address}")
    return host, data


def handle_udp_connection(sock: socket.socket) -> tuple[Host, bytes]:
    """"""
    time.sleep(.5 * random.random())
    data, address = sock.recvfrom(2048)
    host: Host = Host(name='?',
                      mac='?',
                      ip4=(ipaddress.ip_address(address[0]),),
                      os='?')
    print(f"UDP > Received {data} from {address}")
    return host, data
