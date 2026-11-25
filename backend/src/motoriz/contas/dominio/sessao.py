import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Self
from uuid import UUID

from motoriz.compartilhado.ids import novo_id

DURACAO_SESSAO = timedelta(days=14)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@dataclass
class Sessao:
    id: UUID
    conta_id: UUID
    usuario_id: UUID
    token_hash: str
    criada_em: datetime
    expira_em: datetime
    revogada_em: datetime | None

    @classmethod
    def emitir(cls, conta_id: UUID, usuario_id: UUID, agora: datetime) -> tuple[Self, str]:
        if agora.tzinfo is None:
            raise ValueError("agora deve ter fuso horário")
        token = secrets.token_urlsafe(32)
        sessao = cls(
            id=novo_id(),
            conta_id=conta_id,
            usuario_id=usuario_id,
            token_hash=hash_token(token),
            criada_em=agora,
            expira_em=agora + DURACAO_SESSAO,
            revogada_em=None,
        )
        return sessao, token

    def valida_em(self, agora: datetime) -> bool:
        return self.revogada_em is None and agora < self.expira_em

    def revogar(self, agora: datetime) -> None:
        self.revogada_em = agora
