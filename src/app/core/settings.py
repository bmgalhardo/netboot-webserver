from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    netboot_url: str = "http://localhost:8002"

    archs: str = "x86_64"
    alpine_repo: str = "https://dl-cdn.alpinelinux.org/alpine"

    static_folder: str = ""

    database_path: str = ":memory:"

    @model_validator(mode="after")
    def set_database(self):
        self.database_path = f"sqlite:///{self.database_path}"
        return self

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def static_dir(self) -> Path:
        if self.static_folder:
            return Path(self.static_folder)
        else:
            return self.base_dir / "static"

    @property
    def template_dir(self) -> Path:
        return self.base_dir / "front/templates"

    @property
    def alpine_arch_list(self) -> list[str]:
        return self.archs.split(",")


settings = Settings()
