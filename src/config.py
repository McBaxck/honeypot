import time
import logging
from dataclasses import dataclass
from typing import Optional
from src.network.utils import get_public_ip, get_private_ip_and_iface, get_network_ip_with_cidr, get_gateway_ip, \
    scan_network, scan

# CONSTANTS DECLARATION AREA
ONLY_TCP: int = 44
ONLY_UDP: int = 45
HYBRID: int = 46
NO_SHELL_HANDLER: int = -1
SHELL_HANDLER: int = 1
ALL_PORTS: list[int] = [i for i in range(0, 65535)]
DEFAULT_URL_WEBPAGE: str = "https://www.example.com/"
DEFAULT_FILE_WEBPAGE_PATH: str = 'src/protocol/web/cache/index.html'


@dataclass
class HOST:
    PUBLIC: int = 0
    LOCAL: int = 1


@dataclass
class PORT:
    REDIS: int = 6379
    SSH: int = 22
    TELNET: int = 23
    FTP: int = 21


@dataclass
class MODE:
    HYBRID: int = 44
    ONLY_TCP: int = 45
    ONLY_UDP: int = 46


@dataclass
class SHELL:
    ENABLE: int = True
    DISABLE: int = False


@dataclass
class FIREWALL:
    ENABLE: int = True
    DISABLE: int = False


logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


class HolyPotConfig:
    def __init__(self) -> None:
        self.name: str = 'My-Default-Honeypot'
        self.mode: int = MODE.HYBRID
        self.host: int = HOST.PUBLIC
        self.ports: list[int] = []
        self.max_concurrent_connections: int = 5
        self.nodes_cluster: list[str] = []
        self.fw_security: int = FIREWALL.ENABLE


class HostConfig:
    def __init__(self) -> None:
        self._host_pub_ip: Optional[str] = None
        self._host_private_ip: Optional[str] = None
        self._network_ip: Optional[str] = None
        self._network_gtw_ip: Optional[str] = None
        self._host_current_iface: Optional[str] = None
        self._devices: Optional[list] = None
        self._restricted_ports: list[int] = [PORT.REDIS, PORT.SSH, PORT.TELNET, PORT.FTP]
        self._init_settings()

    def _init_settings(self) -> None:
        pass

    @property
    def host_pub_ip(self) -> str:
        return self._host_pub_ip

    @property
    def host_private_ip(self) -> str:
        return self._host_private_ip

    @property
    def network_ip(self) -> str:
        return self._network_ip

    @property
    def network_gtw_ip(self) -> str:
        return self._network_gtw_ip

    @property
    def host_current_iface(self) -> str:
        return self._host_current_iface

    @property
    def devices(self) -> list:
        return self._devices

    def _scan_network(self, network) -> None:
        self._devices = scan(network)


GLOBAL_LOGGING_CONFIG: dict = {
    'version': 1,
    'loggers': {
        'SMTP': {
            'handlers': ['smtp_handler'],
            'level': 'INFO',
        },
        'FTP': {
            'handlers': ['ftp_handler'],
            'level': 'INFO',
        },
        'SSH': {
            'handlers': ['ssh_handler'],
            'level': 'INFO'
        },
        'HTTP': {
            'handlers': ['http_handler'],
            'level': 'INFO'
        },
        'TELNET': {
            'handlers': ['telnet_handler'],
            'level': 'INFO'
        },
        'GLOBAL_SET': {
            'handlers': ['global_set_handler'],
            'level': 'INFO'
        }
    },
    'handlers': {
        'smtp_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'src/protocol/smtp/logs/smtp_server.log'
        },
        'ftp_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'src/protocol/ftp/logs/ftp_server.log'
        },
        'ssh_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'src/protocol/ssh/logs/ssh_server.log'
        },
        'http_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'src/protocol/web/logs/web_server.log'
        },
        'telnet_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'src/protocol/telnet/logs/telnet_server.log'
        },
        'global_set_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'src/global/logs/global.log'
        }
    },
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
}
