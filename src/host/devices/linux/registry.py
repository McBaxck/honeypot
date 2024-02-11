from typing import Any, Optional, Union
from src.host.docker_manager import DockerManager
from abc import ABC, abstractmethod
import random


class Device(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.docker_manager: DockerManager = DockerManager()
        self.os: str = self.__class__.__name__
        self.image: Union[Any, None] = None
        self.tag: Optional[str] = None
        self.dockerfile: Optional[str] = None
        self.id: Optional[str] = None

    @abstractmethod
    def power_on(self) -> None:
        pass

    @abstractmethod
    def power_off(self) -> None:
        pass

    @abstractmethod
    def exec(self, command: str, channel) -> None:
        pass


class Ubuntu(Device):
    def __init__(self) -> None:
        super().__init__()
        self.tag = f'ubuntu-link-hp'
        self.dockerfile = 'Dockerfile-ubuntu'
        self.name = f'UB-{random.randint(1, 10000)}-LIx86_64'
        self.id = self.docker_manager.get_container_id(self.name)
        self._init_device()

    def _init_device(self) -> None:
        self.image = self.docker_manager.build_image_from_dockerfile(
            path='./src/host/devices/linux',
            dockerfile=self.dockerfile,
            tag=self.tag
        )

    def power_on(self) -> None:
        self.docker_manager.run_container(image_name=self.tag,
                                          container_name=self.name)

    def power_off(self) -> None:
        print("Send power_off signal to ubuntu")
        self.docker_manager.stop_container(self.id)

    def exec(self, command: str, channel) -> Any:
        if len(command) > 0:
            return self.docker_manager.exec_command_in_container(container_id_or_name=self.name,
                                                                 command=command, channel=channel)
        else:
            return ''

    def kill(self, p_name: str, channel) -> None:
        return self.docker_manager.kill_all(container_id_or_name=self.name, proc_name=p_name, channel=channel)
