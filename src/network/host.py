import uuid
import ipaddress
from typing import Tuple, Union


class Host(object):
    def __init__(self,
                 name: str,
                 mac: str,
                 ip4: Tuple[ipaddress],
                 os: str) -> None:
        self._id = str(uuid.uuid4())
        self.name: str = name
        self._mac: str = mac
        self._ip4: Tuple[ipaddress] = ip4
        self._os: str = os
        super().__init__()

    @property
    def ip4(self) -> Tuple[ipaddress]:
        return self._ip4

    def lookup(self) -> Union[dict, None]:
        pass

    def ping(self, count: int) -> None:
        pass

    def __dict__(self) -> dict:
        return {
            'name': self.name,
            'mac': self._mac,
            'ip4': list(self._ip4),
            'os': self._os
        }


class LocalHost(Host):
    def __init__(self, name: str, mac: str, ip4: Tuple[ipaddress], os: str) -> None:
        super().__init__(name=name, mac=mac, ip4=ip4, os=os)
        self._ip4: Tuple[ipaddress] = ip4
        self._os: str = ''
        self._mac: str = ''
        self.name: str = self.__class__.__name__.lower()
