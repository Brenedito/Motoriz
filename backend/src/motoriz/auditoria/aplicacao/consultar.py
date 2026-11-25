from uuid import UUID

from motoriz.auditoria.aplicacao.portas import RepositorioDeRegistros
from motoriz.auditoria.dominio.registro import RegistroDeAcao
from motoriz.compartilhado.contexto import ContextoConta, Papel, exigir_papel


class ConsultarTrilha:
    def __init__(self, repositorio: RepositorioDeRegistros) -> None:
        self._repositorio = repositorio

    def executar(
        self, contexto: ContextoConta, entidade: str, entidade_id: UUID
    ) -> list[RegistroDeAcao]:
        exigir_papel(contexto, Papel.ADMIN, Papel.OPERADOR)
        return self._repositorio.listar(contexto.conta_id, entidade, entidade_id)
