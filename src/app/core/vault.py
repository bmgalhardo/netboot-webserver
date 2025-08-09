from pathlib import Path

import requests
from pydantic import BaseModel


class IssuerResponse(BaseModel):
    ca_chain: list[str]
    certificate: str
    expiration: int
    issuing_ca: str
    private_key: str
    private_key_type: str
    serial_number: str


class VaultPKIClient:
    def __init__(self, vault_addr: str, token: str) -> None:
        self.vault_addr = vault_addr.rstrip("/")
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"X-Vault-Token": self.token})
        self.session.verify = (Path(__file__).parent / "./vault_ca").__str__()

    def issue_certificate(
        self, mount: str, common_name: str, role: str = "internal", ttl: str = "8760h"  # 1 year
    ) -> IssuerResponse:
        url = f"{self.vault_addr}/v1/{mount}/issue/{role}"

        payload = {"common_name": common_name, "ttl": ttl}

        response = self.session.post(url, json=payload)
        response.raise_for_status()

        data = response.json()["data"]
        return IssuerResponse(**data)

    @staticmethod
    def write_crt(filename: str, data: IssuerResponse) -> None:
        with open(filename, "w") as f:
            f.write(data.certificate)
            f.write("\n")
            f.write("\n".join(data.ca_chain))

    @staticmethod
    def write_key(filename: str, data: IssuerResponse) -> None:
        with open(filename, "w") as f:
            f.write(data.private_key)

    @staticmethod
    def write_pem(filename: str, data: IssuerResponse) -> None:
        with open(filename, "w") as f:
            f.write(data.private_key)
            f.write("\n")
            f.write(data.certificate)
            f.write("\n")
            f.write("\n".join(data.ca_chain))

    def create_files(self, mount: str, common_name: str, filetype: str = "crt_key") -> None:
        data = self.issue_certificate(mount, common_name)
        if filetype == "crt_key":
            self.write_crt("cert.crt", data)
            self.write_key("cert.key", data)
        elif filetype == "pem":
            self.write_pem("cert.pem", data)
        else:
            raise NotImplementedError
