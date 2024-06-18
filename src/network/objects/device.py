from typing import Optional

from src.network.objects.hostname import CHostname
from src.network.objects.protocol import CProtocol
from src.network.objects.state import CState


class CDevice:
    def __init__(self, **nmap_infos):
        self._root: dict = nmap_infos
        self.__dict__.update(nmap_infos)
        self._init_device_()

    def _init_device_(self) -> None:
        try:
            self._init_device_protocols_()
        except Exception as init_proto_errors:
            # print("Cannot map protocols!")
            pass
        try:
            self._init_device_hostname_()
        except Exception as init_host_errors:
            # print("Cannot map hostnames!")
            pass
        try:
            self._init_device_state_()
        except Exception as init_state_errors:
            # print("Cannot map device state!")
            pass

    def _init_device_protocols_(self):
        try:
            protocols: list[CProtocol] = []
            device_protocols: list[dict] = self._root['datas']['ports']
            for proto in device_protocols:
                protocols.append(CProtocol(**proto))
            self._root['datas']['ports'] = protocols
        except (OSError, KeyError, IndexError):
            print("/!\\ No protocols found in Device {}".format(self.__class__.__name__))
            pass

    def _init_device_hostname_(self):
        try:
            hostnames: list[CHostname] = []
            device_hostnames: list[dict] = self._root['datas']['hostname']
            for host_info in device_hostnames:
                hostnames.append(CHostname(**host_info))
            self._root['datas']['hostname'] = hostnames
        except (OSError, KeyError, IndexError):
            print("/!\\ No hostname found in Device {}".format(self.__class__.__name__))
            pass

    def _init_device_state_(self):
        try:
            device_state: dict = self._root['datas']['state']
            state: Optional[CState] = CState(**device_state)
            self._root['datas']['state'] = state
        except (OSError, KeyError, IndexError):
            print("/!\\ No state_device_info found in Device {}".format(self.__class__.__name__))
            pass
