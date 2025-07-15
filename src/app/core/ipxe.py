from typing import Self

from app.core.settings import settings


class IPXE:

    _shebang = "#!ipxe"
    _netboot_url = settings.netboot_url

    def __init__(self) -> None:
        self._file = [self._shebang, ""]

    def add_msg(self, msg: str) -> Self:
        self._file += [f"echo {msg}"]
        return self

    def add_chain(self, url: str) -> Self:
        self._file += [f"chain {self._netboot_url}/{url.lstrip('/')}"]
        return self

    def set_kernel(self, kernel_location: str, kernel_params: list[str]) -> str:
        url = f"{self._netboot_url}/static/{kernel_location}"
        return f"kernel {url} {' '.join(kernel_params)}"

    def set_initrd(self, initrd_location: str) -> str:
        url = f"{self._netboot_url}/static/{initrd_location}"
        return f"initrd {url}"

    def add_boot(self, kernel_location: str, kernel_params: list[str], initrd_location: str) -> Self:
        self._file += [
            self.set_kernel(kernel_location=kernel_location, kernel_params=kernel_params),
            self.set_initrd(initrd_location),
            "",
            "boot",
        ]
        return self

    def to_file(self):
        return "\n".join(self._file)
