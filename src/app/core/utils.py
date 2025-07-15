import re

from app.core.exceptions import InvalidMAC


class MACAddress:
    def __init__(self, mac: str):
        self.original = mac
        self.normalized = self._normalize(mac)
        if not self._is_valid(self.normalized):
            raise InvalidMAC

    @staticmethod
    def _normalize(mac: str) -> str:
        return re.sub(r"[^a-fA-F0-9]", "", mac).lower()

    @staticmethod
    def _is_valid(mac: str) -> bool:
        return bool(re.fullmatch(r"[0-9a-f]{12}", mac))

    def as_colon(self) -> str:
        return ":".join(self.normalized[i : i + 2] for i in range(0, 12, 2))

    def as_dash(self) -> str:
        return "-".join(self.normalized[i : i + 2] for i in range(0, 12, 2))

    def __str__(self):
        return self.as_colon()
