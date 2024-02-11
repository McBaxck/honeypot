import sys
import typing
import uuid


class Shell(object):
    def __init__(self) -> None:
        super().__init__()
        self.tty: int = 1
        self._id: str = str(uuid.uuid4())
        self._stdout: typing.TextIO = sys.stdout
        self._stderr: typing.TextIO = sys.stderr
        self._stdin: typing.TextIO = sys.stdin
