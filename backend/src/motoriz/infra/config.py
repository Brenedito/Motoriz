from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MOTORIZ_", env_file=".env", extra="ignore")

    url_banco_app: str
    url_banco_migracao: str
    cookie_seguro: bool = True


@lru_cache
def obter_configuracao() -> Configuracao:
    return Configuracao()  # type: ignore[call-arg]
