import datetime
from typing import Any, Union


class History:
    def __init__(self, buffer_size: int) -> None:
        self.buffer_size: int = buffer_size
        self.buffer: dict[str, Any] = {}

    def clear(self) -> str:
        try:
            self.buffer.clear()
            return 'OK'
        except Exception as e:
            return 'ERROR: ' + str(e)

    def store(self, value: str) -> str:
        key: str = datetime.datetime.now().strftime('%Y%m%d%H%M')
        if key not in list(self.buffer.keys()):
            self.buffer[key] = [value]
        else:
            if value not in self.buffer[key]:
                self.buffer[key].append(value)
        return 'OK'

    def retrieve(self, value: str) -> Union[list[str], None]:
        for k, v in self.buffer.items():
            if v in value:
                return self.buffer[k]
            else:
                continue
        return None

    def exists(self, value: str) -> bool:
        if self.retrieve(value) is not None:
            return True
        else:
            return False

    def show(self) -> dict:
        return self.buffer
