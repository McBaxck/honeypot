import os
import select
import socket
from typing import Union, Any
import time
# Custom imports...
from src.network.connection import (create_tcp_socket,
                                    create_udp_socket,
                                    handle_tcp_connection,
                                    handle_udp_connection)
from src.cache.history import History
from src.db.supabase import HoneyPotHandler

# CONSTANTS DECLARATION AREA
ONLY_TCP: int = 44
ONLY_UDP: int = 45
HYBRID: int = 46
NO_SHELL_HANDLER: int = -1
SHELL_HANDLER: int = 1
ALL_PORTS: list[int] = [i for i in range(0, 65535)]


class HoneyPot:
    def __init__(self,
                 name: str,
                 host: str,
                 ports: Union[list[int], str],
                 mode: int = HYBRID,
                 nodes_cluster: list[str] = None,
                 interface: int = NO_SHELL_HANDLER
                 ) -> None:
        """"""
        self._name: str = name
        self._host: str = '0.0.0.0' if host == 'public' else 'localhost'
        self._ports: Union[list[int], str] = ports if ports != 'all' else ALL_PORTS
        self._mode: int = mode
        self._nodes_cluster: list[str] = nodes_cluster
        self._interface: int = interface
        self.poller: select.poll = select.poll()
        self.fd_to_socket: dict = {}
        self._history: History = History(buffer_size=4096)
        self._db: HoneyPotHandler = HoneyPotHandler()

    @property
    def name(self) -> str:
        return self._name

    @property
    def host(self) -> str:
        return self._host

    @property
    def ports(self) -> list[int]:
        return self._ports

    @property
    def mode(self) -> int:
        return self._mode

    def _init_poller(self) -> None:
        """"""
        for port in self._ports:
            # CREATE TCP AND UDP SOCKETS
            tcp_socket: socket.socket = create_tcp_socket(self._host, port)
            udp_socket: socket.socket = create_udp_socket(self._host, port)
            # REGISTER IT IN THE CURRENT POLLER
            self.poller.register(tcp_socket, select.POLLIN)
            self.poller.register(udp_socket, select.POLLIN)
            # APPEND IT IN THE FD_SOCKS ARRAY
            self.fd_to_socket[tcp_socket.fileno()] = tcp_socket
            self.fd_to_socket[udp_socket.fileno()] = udp_socket

    def wait_for_connections(self) -> None:
        """"""
        while 1:
            events: list = self.poller.poll(1000)
            for fd, event in events:
                sock: socket.socket = self.fd_to_socket[fd]
                if event & select.POLLIN:
                    # TCP ---------------------------------
                    if sock.type == socket.SOCK_STREAM:
                        host, data = handle_tcp_connection(sock)
                        log: dict[str, Any] = {'type': 'tcp',
                                               'source_ip': host.ip4[0].__str__(),
                                               'source_port': 0,
                                               'data': data.decode(),
                                               'dest_port': 1,
                                               'dest_ip': self._host,
                                               'protocol': '?'}
                        self._db.add_log(log)
                        self._history.store(host.ip4[0])
                    # UDP ---------------------------------
                    if sock.type == socket.SOCK_DGRAM:
                        host, data = handle_udp_connection(sock)
                        log: dict[str, Any] = {'type': 'udp',
                                               'source_ip': host.ip4[0].__str__(),
                                               'source_port': 0,
                                               'data': data.decode(),
                                               'dest_port': 1,
                                               'dest_ip': self._host,
                                               'protocol': '?'}
                        self._db.add_log(log)
                        self._history.store(host.ip4[0])
                print(self._history.show())

    def run(self) -> None:
        """"""
        self._init_poller()
        print("[•] Starting HP...")
        try:
            self.wait_for_connections()
        except KeyboardInterrupt:
            self.shutdown()
        finally:
            print('Bye :)')

    def shutdown(self) -> None:
        self.fd_to_socket.clear()
        print("Quitting...")
        time.sleep(2.0)
        quit(os.EX_OK)
