import re
import tarfile
import tempfile
from pathlib import Path
from urllib.parse import urljoin

import requests
from packaging.version import Version

from app.core.settings import settings


class AlpineAssets:

    _repo = settings.alpine_repo

    def __init__(self, arch: str, version: str) -> None:
        self.arch = arch
        self.version = version

    @classmethod
    def list_versions(cls) -> list[str]:
        response = requests.get(url=cls._repo, timeout=5)

        versions = re.findall(r"\d+\.\d+/", response.text)
        versions = sorted(set(v.rstrip("/") for v in versions), key=Version, reverse=True)

        return versions

    @property
    def _filename(self) -> str:
        return f"alpine-netboot-{self.version}.0-{self.arch}.tar.gz"

    @property
    def _url(self) -> str:
        url = urljoin(self._repo, f"v{self.version}/releases/{self.arch}/{self._filename}")
        return url

    def download(self, output_path: Path) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            response = requests.get(self._url, stream=True, timeout=5)

            if response.status_code != 200:
                print(f"not found: {self._url}")
                raise FileNotFoundError

            downloaded_file = Path(tmpdir) / self._filename
            with open(downloaded_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.extract(file_path=downloaded_file, output_path=output_path)

    @staticmethod
    def extract(file_path: Path, output_path: Path) -> None:
        if not output_path.exists():
            output_path.mkdir(parents=True)

        if tarfile.is_tarfile(file_path):
            with tarfile.open(file_path, "r:gz") as tar:
                tar.extractall(path=output_path)  # nosec
        else:
            print("unexpected format")
