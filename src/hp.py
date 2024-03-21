import ipaddress
import os
import select
import socket
import ssl
import threading
import datetime
from typing import Union, Any
# CUSTOM IMPORTS -------------------
from src.config import *
from src.firewall.embedded_fw import EmbeddedFirewall
from src.network.connection import (create_tcp_socket,
                                    create_udp_socket,
                                    handle_tcp_connection,
                                    handle_udp_connection)
from src.cache.history import History
from src.db.supabase import HoneyPotHandler
from src.protocol.detector.detector import detect_protocol
from src.protocol.ssh.ssh import FakeSSHServer
from src.host import nslookup_with_geolocation
from src.protocol.telnet.telnet import FakeTelnetServer
from src.protocol.web.server import launch_web_server
from src.protocol.ftp.ftp import FakeFTPServer
from src.protocol.smtp.smtp import start_smtp

global_logger = logging.getLogger('GLOBAL_SET')


class HolyPot:
    def __init__(self, holypot_config: HolyPotConfig) -> None:
        """HoneyPot Device Simulation"""
        global_logger.info('Booting the current honeypot instance...')
        self._name: str = holypot_config.name
        global_logger.info('Set $NAME -> %s', self._name)
        self._host: str = '0.0.0.0' if holypot_config.host == HOST.PUBLIC else 'localhost'
        global_logger.info('Set $HOSTNAME -> %s', self._host)
        self._ports: Union[list[int], str] = holypot_config.ports if holypot_config.ports != 'all' else ALL_PORTS
        global_logger.info('Set $PORTS -> %s' % self._ports)
        self._mode: int = holypot_config.mode
        global_logger.info('Set $MODE -> %s', self._mode)
        self._nodes_cluster: list[str] = holypot_config.nodes_cluster
        global_logger.info('Set $CLUSTER_NODES -> %s', self._nodes_cluster)
        self.poller: select.poll = select.poll()
        self.fd_to_socket: dict = {}
        self._history: History = History(buffer_size=4096)
        global_logger.info('Init an empty history buffer (BUF_SIZE=4096)...')
        self._db: HoneyPotHandler = HoneyPotHandler()
        self._fw: EmbeddedFirewall = EmbeddedFirewall(is_active=holypot_config.fw_security)
        self.config: HolyPotConfig = holypot_config
        global_logger.info('Importing default configurations...')
        self._active_threads: list[threading.Thread] = []
        global_logger.info('Initializing threads stack...')

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
                        global_logger.info('Received a connection from: %s', sock.fileno())
                        self._tcp(sock)
                    # UDP ---------------------------------
                    if sock.type == socket.SOCK_DGRAM:
                        global_logger.info('Received a message from %s', sock.fileno())
                        self._udp(sock)
                    if sock.type == ssl.SSLSocket:
                        global_logger.info("SSL handshake")
                global_logger.info("Current History -> ", self._history.show())

    def add_service(self, on_ports: list[int], service: str) -> None:
        for port in on_ports:
            if 65535 >= port > 0:
                if port in self._ports:
                    self._ports.remove(port)
                if service == 'ssh':
                    global_logger.info('Adding service <SSH> to port: %s' % port)
                    ssh_server: FakeSSHServer = FakeSSHServer(host_key='./src/host/.ssh/test_rsa')
                    ssh_server_thread = threading.Thread(target=ssh_server.start_server, args=(self._host, port))
                    ssh_server_thread.start()
                    self._active_threads.append(ssh_server_thread)
                if service == 'telnet':
                    global_logger.info('Adding service <Telnet> to port: %s' % port)
                    telnet_server: FakeTelnetServer = FakeTelnetServer(host=self._host, port=port)
                    telnet_server_thread = threading.Thread(target=telnet_server.start)
                    telnet_server_thread.start()
                if service == 'http':
                    global_logger.info('Adding service <HTTP> to port: %s' % port)
                    web_server_thread: threading.Thread = threading.Thread(target=launch_web_server,
                                                                           args=(DEFAULT_URL_WEBPAGE, port))
                    web_server_thread.start()
                    self._active_threads.append(web_server_thread)
                if service == 'ftp':
                    global_logger.info('Adding service <FTP> to port: %s' % port)
                    ftp_server: FakeFTPServer = FakeFTPServer(port=port)
                    ftp_server_thread: threading.Thread = threading.Thread(target=ftp_server.start_server)
                    ftp_server_thread.start()
                    self._active_threads.append(ftp_server_thread)
                if service == 'smtp':
                    global_logger.info('Adding service <SMTP> to port: %s' % port)
                    smtp_server_thread: threading.Thread = threading.Thread(target=start_smtp,
                                                                            args=(port,))
                    smtp_server_thread.start()
                    self._active_threads.append(smtp_server_thread)

    def _tcp(self, sock: socket.socket) -> None:
        host, data, client, peer = handle_tcp_connection(sock)
        client_ip, client_port = sock.getsockname()
        try:
            global_logger.info('Registering TCP connection <%s:%d>' % (host, client_port))
            self.register_in_database('tcp', str(client_ip), client_port, data.decode(),
                                      peer[1], self._host)
        except ConnectionRefusedError:
            global_logger.info("Connection refused, pass...")
        except UnicodeDecodeError:
            global_logger.info("Error_Retry>>> registering TCP connection <%s:%d>" % (host, client_port))
            self.register_in_database('tcp', str(client_ip), client_port, str(data),
                                      peer[1], self._host)
        self._history.store(host.ip4[0])
        self._fw.add_connection(host.ip4[0].__str__())

    def _udp(self, sock: socket.socket) -> None:
        host, data, client = handle_udp_connection(sock)

        self.register_in_database('udp', host.ip4[0].__str__(), client[1],
                                  data.decode(), 0, self._host)
        self._history.store(host.ip4[0])
        self._fw.add_connection(host.ip4[0].__str__())

    def register_in_database(self, communication_type: str, source_ip: str, source_port: int,
                             data: str, dest_port: int, dest_ip: str) -> None:
        if ipaddress.IPv4Address(dest_ip).is_global:
            country: str = nslookup_with_geolocation(dest_ip)
        elif ipaddress.IPv4Address(dest_ip).is_private:
            country: str = "LOCAL_POS"
        else:
            country: str = "??"
        log: dict[str, Any] = {
            'type': communication_type,
            'source_ip': source_ip,
            'source_port': source_port,
            'data': data,
            'dest_port': dest_port,
            'dest_ip': dest_ip,
            'protocol': detect_protocol(data),
            'country': country
        }
        self._db.add_log(log)

    def run(self) -> None:
        """"""
        self._init_poller()
        global_logger.info("Current [active] threads up: " + str(self._active_threads))
        print("[•] Welcome to the HolyPot Interface!")
        try:
            print("[---] HolyPot is waiting for connections...")
            self.wait_for_connections()
        except KeyboardInterrupt:
            print("[---] Say goodbye to HolyPot! See ya!")
            self.shutdown()
        finally:
            print('> Ended at {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def shutdown(self) -> None:
        self.fd_to_socket.clear()
        global_logger.info("Quitting...")
        time.sleep(2.0)
        return
