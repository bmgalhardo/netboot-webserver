from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    netboot_url: str = "http://netboot.bgalhardo.internal"

settings = Settings()
