from datetime import UTC, datetime, timedelta

import pytest

from motoriz.compartilhado.ids import novo_id
from motoriz.contas.dominio.sessao import Sessao, hash_token


def test_sessao_expira_em_14_dias():
    agora = datetime(2026, 11, 24, 12, tzinfo=UTC)
    sessao, token = Sessao.emitir(novo_id(), novo_id(), agora)
    assert sessao.token_hash == hash_token(token) and token not in sessao.token_hash
    assert sessao.valida_em(agora + timedelta(days=14) - timedelta(seconds=1))
    assert not sessao.valida_em(agora + timedelta(days=14))


def test_sessao_revogada_nao_vale():
    agora = datetime(2026, 11, 24, tzinfo=UTC)
    sessao, _ = Sessao.emitir(novo_id(), novo_id(), agora)
    sessao.revogar(agora)
    assert not sessao.valida_em(agora)


def test_emitir_exige_data_com_fuso():
    with pytest.raises(ValueError):
        Sessao.emitir(novo_id(), novo_id(), datetime(2026, 11, 24))


def test_tokens_sao_diferentes_e_hash_e_sha256_hex():
    agora = datetime(2026, 11, 24, tzinfo=UTC)
    _, t1 = Sessao.emitir(novo_id(), novo_id(), agora)
    _, t2 = Sessao.emitir(novo_id(), novo_id(), agora)
    assert t1 != t2
    assert len(hash_token(t1)) == 64
