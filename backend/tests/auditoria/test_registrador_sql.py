from datetime import UTC, datetime
from enum import StrEnum

import pytest

from motoriz.auditoria.adaptadores.registrador_sql import RegistradorSql
from motoriz.auditoria.aplicacao.consultar import ConsultarTrilha
from motoriz.compartilhado.contexto import Ator, ContextoConta, Papel
from motoriz.compartilhado.ids import novo_id

pytestmark = pytest.mark.banco


def test_registra_e_consulta_mascarado(sessao, relogio_fixo):
    ator = Ator(conta_id=novo_id(), usuario_id=novo_id(), origem="usuario")
    alvo = novo_id()
    RegistradorSql(sessao, relogio_fixo).registrar(
        ator,
        "usuario.criado",
        "usuario",
        alvo,
        depois={"nome": "Ana", "papel": "operador"},
        campos_pessoais=frozenset({"nome"}),
    )
    [r] = RegistradorSql(sessao, relogio_fixo).listar(ator.conta_id, "usuario", alvo)
    assert r.depois == {"nome": "[dado pessoal]", "papel": "operador"}
    assert r.antes is None
    assert r.registrado_em == relogio_fixo.agora()
    assert r.origem == "usuario"


def test_converte_valores_de_dominio_para_json(sessao, relogio_fixo):
    class Cor(StrEnum):
        AZUL = "azul"

    ator = Ator(conta_id=novo_id(), usuario_id=None, origem="sistema")
    alvo, outro = novo_id(), novo_id()
    instante = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)
    RegistradorSql(sessao, relogio_fixo).registrar(
        ator, "x.mudou", "x", alvo, depois={"id": outro, "quando": instante, "cor": Cor.AZUL}
    )
    [r] = RegistradorSql(sessao, relogio_fixo).listar(ator.conta_id, "x", alvo)
    assert r.depois == {"id": str(outro), "quando": instante.isoformat(), "cor": "azul"}


def test_consulta_nao_ve_outra_conta(sessao, relogio_fixo):
    ator_a = Ator(conta_id=novo_id(), usuario_id=novo_id(), origem="usuario")
    assert ator_a.conta_id is not None
    alvo = novo_id()
    registrador = RegistradorSql(sessao, relogio_fixo)
    registrador.registrar(ator_a, "usuario.criado", "usuario", alvo)
    contexto_b = ContextoConta(conta_id=novo_id(), usuario_id=novo_id(), papel=Papel.ADMIN)
    assert ConsultarTrilha(registrador).executar(contexto_b, "usuario", alvo) == []
    contexto_a = ContextoConta(conta_id=ator_a.conta_id, usuario_id=novo_id(), papel=Papel.ADMIN)
    assert len(ConsultarTrilha(registrador).executar(contexto_a, "usuario", alvo)) == 1
