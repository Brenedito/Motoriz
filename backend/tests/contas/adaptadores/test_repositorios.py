from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool

from motoriz.compartilhado.contexto import Papel
from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.email import Email
from motoriz.compartilhado.erros import NaoEncontrado
from motoriz.compartilhado.ids import novo_id
from motoriz.compartilhado.relogio import RelogioFixo
from motoriz.contas.adaptadores.orm import LocadoraOrm, SessaoOrm, UsuarioOrm
from motoriz.contas.adaptadores.repositorios import (
    RepositorioLocadorasSql,
    RepositorioSessoesSql,
    RepositorioUsuariosSql,
)
from motoriz.contas.dominio.erros import EmailJaCadastrado, LocadoraJaCadastrada
from motoriz.contas.dominio.locadora import Locadora, SituacaoLocadora
from motoriz.contas.dominio.sessao import Sessao
from motoriz.contas.dominio.usuario import Usuario
from motoriz.infra.banco import criar_fabrica
from motoriz.infra.conta import definir_conta, modo_plataforma

pytestmark = pytest.mark.banco

AGORA = datetime(2026, 11, 24, 12, 30, 15, 123456, tzinfo=UTC)


def novo_usuario(conta_id, email="ana@x.com", nome="Ana", papel=Papel.OPERADOR) -> Usuario:
    return Usuario.novo(conta_id, nome, Email.de(email), papel, "hash-argon2")


# --- Locadoras -------------------------------------------------------------------------------


def test_locadora_ida_e_volta(sessao):
    repo = RepositorioLocadorasSql(sessao, relogio=RelogioFixo(AGORA))
    loc = Locadora.nova("Locadora Y", Documento.de("529.982.247-25"), "y@locadora.com")
    repo.adicionar(loc)
    sessao.expunge_all()
    assert repo.obter(loc.id) == loc
    assert repo.obter_por_documento(Documento.de("52998224725")) == loc
    orm = sessao.get(LocadoraOrm, loc.id)
    assert orm.criada_em == AGORA


def test_locadora_salvar(sessao, locadora_gravada):
    repo = RepositorioLocadorasSql(sessao)
    locadora_gravada.suspender()
    locadora_gravada.nome = "Novo nome"
    repo.salvar(locadora_gravada)
    sessao.expunge_all()
    lida = repo.obter(locadora_gravada.id)
    assert lida.situacao is SituacaoLocadora.SUSPENSA
    assert lida.nome == "Novo nome"


def test_locadora_inexistente(sessao):
    repo = RepositorioLocadorasSql(sessao)
    assert repo.obter_por_documento(Documento.de("11444777000161")) is None


def test_documento_de_locadora_e_unico(sessao, locadora_gravada):
    # A checagem prévia do caso de uso não fecha a corrida entre duas criações simultâneas:
    # quem perde bate na unique do banco, e o repositório traduz para o erro de domínio (409).
    repo = RepositorioLocadorasSql(sessao)
    with pytest.raises(LocadoraJaCadastrada):
        repo.adicionar(Locadora.nova("Outra", locadora_gravada.documento, "o@o.com"))


def test_bloquear_locadora_segura_a_linha_ate_o_fim_da_transacao(motor_app, conta_a):
    # Duas conexões de verdade (sem pool, para o tempo de espera curto não vazar para outros
    # testes): enquanto a primeira segura o bloqueio, a segunda não o obtém.
    motor = create_engine(motor_app.url, poolclass=NullPool)
    fabrica = criar_fabrica(motor)
    try:
        with fabrica() as primeira, fabrica() as segunda:
            modo_plataforma(primeira)
            modo_plataforma(segunda)
            RepositorioLocadorasSql(primeira).bloquear(conta_a.conta_id)
            segunda.execute(text("SET SESSION innodb_lock_wait_timeout = 1"))
            with pytest.raises(OperationalError):
                RepositorioLocadorasSql(segunda).bloquear(conta_a.conta_id)
            segunda.rollback()
            primeira.rollback()
            # Solto o bloqueio, a segunda consegue.
            modo_plataforma(segunda)
            RepositorioLocadorasSql(segunda).bloquear(conta_a.conta_id)
            segunda.rollback()
    finally:
        motor.dispose()


def test_bloquear_locadora_inexistente(sessao):
    with pytest.raises(NaoEncontrado, match="Locadora não encontrada"):
        RepositorioLocadorasSql(sessao).bloquear(novo_id())


# --- Usuários --------------------------------------------------------------------------------


def test_usuario_ida_e_volta(sessao, locadora_gravada):
    definir_conta(sessao, locadora_gravada.id)
    repo = RepositorioUsuariosSql(sessao, relogio=RelogioFixo(AGORA))
    u = novo_usuario(locadora_gravada.id, papel=Papel.ADMIN)
    repo.adicionar(u)
    sessao.expunge_all()
    lido = repo.obter(u.id)
    assert lido == u
    assert isinstance(lido.email, Email)
    assert lido.papel is Papel.ADMIN
    orm = sessao.scalars(select(UsuarioOrm)).one()
    assert orm.versao == 1
    assert orm.criado_em == AGORA


def test_usuario_salvar_incrementa_versao(sessao, locadora_gravada):
    definir_conta(sessao, locadora_gravada.id)
    repo = RepositorioUsuariosSql(sessao)
    u = novo_usuario(locadora_gravada.id)
    repo.adicionar(u)
    u.desativar()
    u.trocar_hash_senha("outro-hash")
    repo.salvar(u)
    sessao.expunge_all()
    assert repo.obter(u.id) == u
    assert sessao.scalars(select(UsuarioOrm.versao)).one() == 2


def test_usuario_de_outra_conta_nao_e_encontrado(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    repo = RepositorioUsuariosSql(sessao)
    assert repo.obter(b.usuario_id) is None
    assert repo.obter(a.usuario_id) is not None


def test_email_unico_ignorando_caixa(sessao, locadora_gravada):
    definir_conta(sessao, locadora_gravada.id)
    repo = RepositorioUsuariosSql(sessao)
    repo.adicionar(novo_usuario(locadora_gravada.id, "ana@x.com"))
    assert repo.email_em_uso(Email.de("ANA@x.com")) is True
    assert repo.email_em_uso(Email.de("bia@x.com")) is False


def test_email_em_uso_olha_todas_as_contas(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    repo = RepositorioUsuariosSql(sessao)
    assert repo.email_em_uso(Email.de(b.email)) is True
    encontrado = repo.obter_por_email_em_todas_as_contas(Email.de(b.email))
    assert encontrado is not None
    assert encontrado.conta_id == b.conta_id


def test_email_unico_na_plataforma(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    repo = RepositorioUsuariosSql(sessao)
    with pytest.raises(EmailJaCadastrado):
        repo.adicionar(novo_usuario(a.conta_id, b.email))


def test_obter_por_email_sem_conta_definida(sessao, duas_contas):
    a, _ = duas_contas
    repo = RepositorioUsuariosSql(sessao)
    encontrado = repo.obter_por_email_em_todas_as_contas(Email.de(a.email))
    assert encontrado is not None
    assert encontrado.id == a.usuario_id
    assert repo.obter_por_email_em_todas_as_contas(Email.de("ninguem@x.com")) is None


def test_listar_ordena_por_nome_e_filtra_conta(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    repo = RepositorioUsuariosSql(sessao)
    repo.adicionar(novo_usuario(a.conta_id, "caio@x.com", "Caio"))
    repo.adicionar(novo_usuario(a.conta_id, "bia@x.com", "Bia"))
    assert [u.nome for u in repo.listar()] == ["Ana", "Bia", "Caio"]


def test_contar_admins_ativos_ignora_inativos(sessao, locadora_gravada):
    definir_conta(sessao, locadora_gravada.id)
    repo = RepositorioUsuariosSql(sessao)
    conta = locadora_gravada.id
    repo.adicionar(novo_usuario(conta, "a1@x.com", papel=Papel.ADMIN))
    inativo = novo_usuario(conta, "a2@x.com", papel=Papel.ADMIN)
    repo.adicionar(inativo)
    inativo.desativar()
    repo.salvar(inativo)
    repo.adicionar(novo_usuario(conta, "op@x.com", papel=Papel.OPERADOR))
    assert repo.contar_admins_ativos() == 1


def test_contar_admins_ativos_so_da_conta(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, b.conta_id)
    RepositorioUsuariosSql(sessao).adicionar(
        novo_usuario(b.conta_id, "adm@b.com", papel=Papel.ADMIN)
    )
    definir_conta(sessao, a.conta_id)
    assert RepositorioUsuariosSql(sessao).contar_admins_ativos() == 0


# --- Sessões ---------------------------------------------------------------------------------


@pytest.fixture
def usuario_gravado(sessao, locadora_gravada) -> Usuario:
    definir_conta(sessao, locadora_gravada.id)
    u = novo_usuario(locadora_gravada.id)
    RepositorioUsuariosSql(sessao).adicionar(u)
    return u


def test_sessao_ida_e_volta(sessao, usuario_gravado):
    repo = RepositorioSessoesSql(sessao)
    s, _ = Sessao.emitir(usuario_gravado.conta_id, usuario_gravado.id, AGORA)
    repo.adicionar(s)
    sessao.expunge_all()
    sessao.info.clear()
    lida = repo.obter_por_hash_em_todas_as_contas(s.token_hash)
    assert lida == s
    assert lida.criada_em.tzinfo is not None
    assert repo.obter_por_hash_em_todas_as_contas("0" * 64) is None


def test_sessao_salvar(sessao, usuario_gravado):
    repo = RepositorioSessoesSql(sessao)
    s, _ = Sessao.emitir(usuario_gravado.conta_id, usuario_gravado.id, AGORA)
    repo.adicionar(s)
    s.revogar(AGORA + timedelta(hours=1))
    repo.salvar(s)
    sessao.expunge_all()
    assert repo.obter_por_hash_em_todas_as_contas(s.token_hash) == s


def test_revogar_do_usuario_revoga_todas(sessao, usuario_gravado):
    repo = RepositorioSessoesSql(sessao)
    s1, _ = Sessao.emitir(usuario_gravado.conta_id, usuario_gravado.id, AGORA)
    s2, _ = Sessao.emitir(usuario_gravado.conta_id, usuario_gravado.id, AGORA)
    repo.adicionar(s1)
    repo.adicionar(s2)
    quando = AGORA + timedelta(minutes=5)
    repo.revogar_do_usuario(usuario_gravado.id, quando)
    for s in (s1, s2):
        lida = repo.obter_por_hash_em_todas_as_contas(s.token_hash)
        assert lida is not None
        assert lida.revogada_em == quando


def test_revogar_do_usuario_nao_reescreve_revogadas(sessao, usuario_gravado):
    repo = RepositorioSessoesSql(sessao)
    antiga, _ = Sessao.emitir(usuario_gravado.conta_id, usuario_gravado.id, AGORA)
    antiga.revogar(AGORA)
    repo.adicionar(antiga)
    repo.revogar_do_usuario(usuario_gravado.id, AGORA + timedelta(days=1))
    assert repo.obter_por_hash_em_todas_as_contas(antiga.token_hash).revogada_em == AGORA


def test_revogar_do_usuario_deixa_objetos_carregados_legiveis(sessao, usuario_gravado):
    repo = RepositorioSessoesSql(sessao)
    s1, _ = Sessao.emitir(usuario_gravado.conta_id, usuario_gravado.id, AGORA)
    s2, _ = Sessao.emitir(usuario_gravado.conta_id, usuario_gravado.id, AGORA)
    repo.adicionar(s1)
    repo.adicionar(s2)
    carregadas = sessao.scalars(select(SessaoOrm).order_by(SessaoOrm.id)).all()
    sessao.expire(carregadas[0])  # já expirada antes: o repositório não pode tropeçar nela
    quando = AGORA + timedelta(minutes=1)
    repo.revogar_do_usuario(usuario_gravado.id, quando)
    assert [s.revogada_em for s in carregadas] == [quando, quando]
    assert {s.usuario_id for s in carregadas} == {usuario_gravado.id}


def test_revogar_do_usuario_poupa_a_sessao_excecao(sessao, usuario_gravado):
    repo = RepositorioSessoesSql(sessao)
    atual, _ = Sessao.emitir(usuario_gravado.conta_id, usuario_gravado.id, AGORA)
    outra, _ = Sessao.emitir(usuario_gravado.conta_id, usuario_gravado.id, AGORA)
    repo.adicionar(atual)
    repo.adicionar(outra)
    quando = AGORA + timedelta(minutes=5)
    repo.revogar_do_usuario(usuario_gravado.id, quando, exceto_hash=atual.token_hash)
    assert repo.obter_por_hash_em_todas_as_contas(atual.token_hash).revogada_em is None
    assert repo.obter_por_hash_em_todas_as_contas(outra.token_hash).revogada_em == quando


def test_obter_usuario_em_todas_as_contas_sem_conta_definida(sessao, duas_contas):
    a, b = duas_contas
    repo = RepositorioUsuariosSql(sessao)
    assert repo.obter_em_todas_as_contas(a.usuario_id).conta_id == a.conta_id
    assert repo.obter_em_todas_as_contas(b.usuario_id).conta_id == b.conta_id
    assert repo.obter_em_todas_as_contas(novo_id()) is None


def test_plataforma_le_locadora_e_usuarios(sessao, duas_contas):
    a, b = duas_contas
    modo_plataforma(sessao)
    # Contém as duas contas; o banco pode ter outras, gravadas pelos testes de API.
    ids = {u.id for u in RepositorioUsuariosSql(sessao).listar()}
    assert {a.usuario_id, b.usuario_id} <= ids
