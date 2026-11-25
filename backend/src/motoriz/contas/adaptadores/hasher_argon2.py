from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError


class HasherArgon2:
    """Argon2id com os parâmetros padrão do `argon2-cffi`."""

    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def gerar(self, senha: str) -> str:
        return self._hasher.hash(senha)

    def verificar(self, senha: str, hash: str) -> bool:
        try:
            return self._hasher.verify(hash, senha)
        except (VerificationError, InvalidHashError):
            return False
