from pathlib import Path

import yaml
import requests

from app.utils import MACAddress

class Schematic:

    def __init__(self):
        self._config = self._read_config()

    @staticmethod
    def _read_config() -> dict:
        config_path = Path(__file__).parent / "config.yml"
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    @property
    def talos_version(self) -> str:
        return self._config["talosVersion"]

    def mac_to_schematic(self, mac: MACAddress) -> dict:
        mac_filter = mac.as_dash()[:-3]
        return self._config[mac_filter]

    @staticmethod
    def schematic_to_id(schematic: dict) -> str:
        response = requests.post("https://factory.talos.dev/schematics", json=schematic)
        image_id = response.json()["id"]
        return image_id

    def mac_to_id(self, mac: MACAddress) -> str:
        schematic = self.mac_to_schematic(mac)
        return self.schematic_to_id(schematic)

    def mac_to_factory_url(self, mac: MACAddress) -> str:
        image_id = self.mac_to_id(mac)
        url = f"https://pxe.factory.talos.dev/pxe/{image_id}/{self.talos_version}/metal-amd64"
        return url
