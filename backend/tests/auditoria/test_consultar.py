from datetime import UTC, datetime
from uuid import UUID

import pytest
from fakes.auditoria import RegistradorEmMemoria

from motoriz.auditoria.aplicacao.consultar import ConsultarTrilha
from motoriz.compartilhado.contexto import Ator, ContextoConta, Papel
from motoriz.compartilhado.erros import AcessoNegado
from motoriz.compartilhado.ids import novo_id


def _contexto(conta_id: UUID, papel: Papel = Papel.ADMIN) -> ContextoConta:
    return ContextoConta(conta_id=conta_id, usuario_id=novo_id(), papel=papel)


def test_consulta_so_registros_da_conta_em_ordem():
    repo = RegistradorEmMemoria()
    conta, outra, alvo = novo_id(), novo_id(), novo_id()
    repo.registrar(Ator(conta, None, "usuario"), "a.um", "usuario", alvo)
    repo.registrar(Ator(outra, None, "usuario"), "a.dois", "usuario", alvo)
    repo.registrar(Ator(conta, None, "usuario"), "a.tres", "usuario", alvo)
    trilha = ConsultarTrilha(repo).executar(_contexto(conta), "usuario", alvo)
    assert [r.acao for r in trilha] == ["a.um", "a.tres"]


def test_operador_pode_consultar():
    resultado = ConsultarTrilha(RegistradorEmMemoria()).executar(
        _contexto(novo_id(), Papel.OPERADOR), "usuario", novo_id()
    )
    assert resultado == []


def test_papel_fora_de_admin_e_operador_e_negado():
    contexto = _contexto(novo_id())
    object.__setattr__(contexto, "papel", "visitante")
    with pytest.raises(AcessoNegado):
        ConsultarTrilha(RegistradorEmMemoria()).executar(contexto, "usuario", novo_id())


def test_registrado_em_vem_do_relogio():
    repo = RegistradorEmMemoria()
    repo.registrar(Ator(novo_id(), None, "sistema"), "x", "usuario", novo_id())
    assert repo.registros[0].registrado_em == datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
