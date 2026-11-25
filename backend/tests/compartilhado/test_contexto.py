from datetime import UTC, datetime, timedelta

import pytest

from motoriz.compartilhado.contexto import ContextoConta, Papel, exigir_papel
from motoriz.compartilhado.erros import AcessoNegado
from motoriz.compartilhado.ids import novo_id
from motoriz.compartilhado.relogio import RelogioDoSistema, RelogioFixo


def test_exigir_papel_bloqueia_operador() -> None:
    ctx = ContextoConta(conta_id=novo_id(), usuario_id=novo_id(), papel=Papel.OPERADOR)
    with pytest.raises(AcessoNegado) as erro:
        exigir_papel(ctx, Papel.ADMIN)
    assert erro.value.mensagem == "Ação não permitida para o seu perfil"


def test_exigir_papel_aceita_papel_listado() -> None:
    ctx = ContextoConta(conta_id=novo_id(), usuario_id=novo_id(), papel=Papel.ADMIN)
    exigir_papel(ctx, Papel.ADMIN, Papel.OPERADOR)


def test_ator_do_contexto_e_usuario() -> None:
    ctx = ContextoConta(conta_id=novo_id(), usuario_id=novo_id(), papel=Papel.ADMIN)
    assert ctx.ator.origem == "usuario"
    assert (ctx.ator.conta_id, ctx.ator.usuario_id) == (ctx.conta_id, ctx.usuario_id)


def test_ids_sao_ordenaveis_no_tempo() -> None:
    a, b = novo_id(), novo_id()
    assert a.version == 7 and a < b


def test_relogio_fixo_avanca() -> None:
    inicio = datetime(2026, 1, 1, tzinfo=UTC)
    relogio = RelogioFixo(inicio)
    relogio.avancar(timedelta(hours=1))
    assert relogio.agora() == inicio + timedelta(hours=1)


def test_relogio_do_sistema_e_utc() -> None:
    assert RelogioDoSistema().agora().utcoffset() == timedelta(0)
