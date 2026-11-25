import pytest

from motoriz.compartilhado.contexto import ContextoConta, Papel
from motoriz.compartilhado.erros import AcessoNegado, NaoEncontrado, RegraViolada
from motoriz.contas.dominio.erros import EmailJaCadastrado, SenhaFraca

SENHA = "senha-segura-1"


def test_operador_nao_cria_usuario(cenario):
    with pytest.raises(AcessoNegado):
        cenario.criar.executar(cenario.ctx_operador, "Bia", "bia@x.com", Papel.OPERADOR, SENHA)


def test_criar_usuario(cenario):
    u = cenario.criar.executar(cenario.ctx_admin, "Bia", " Bia@X.com ", Papel.OPERADOR, SENHA)
    salvo = cenario.usuarios.obter(u.id)
    assert salvo is not None
    assert (salvo.conta_id, salvo.email.valor, salvo.papel, salvo.ativo) == (
        cenario.locadora.id,
        "bia@x.com",
        Papel.OPERADOR,
        True,
    )
    assert salvo.hash_senha == "hash:" + SENHA


def test_email_duplicado_na_mesma_conta(cenario):
    with pytest.raises(EmailJaCadastrado):
        cenario.criar.executar(
            cenario.ctx_admin, "Outra Ana", "ANA@locadora.com", Papel.OPERADOR, SENHA
        )


def test_email_duplicado_em_outra_conta(cenario):
    with pytest.raises(EmailJaCadastrado):
        cenario.criar.executar(cenario.ctx_admin, "Duda 2", "duda@norte.com", Papel.OPERADOR, SENHA)


def test_criar_usuario_com_senha_fraca(cenario):
    with pytest.raises(SenhaFraca):
        cenario.criar.executar(cenario.ctx_admin, "Bia", "bia@x.com", Papel.OPERADOR, "curta")
    assert cenario.auditoria.registros == []


def test_criar_usuario_audita_sem_dado_pessoal(cenario):
    u = cenario.criar.executar(cenario.ctx_admin, "Bia", "bia@x.com", Papel.OPERADOR, SENHA)
    r = cenario.auditoria.registros[-1]
    assert (r.acao, r.entidade, r.entidade_id) == ("usuario.criado", "usuario", u.id)
    assert r.depois == {
        "nome": "[dado pessoal]",
        "email": "[dado pessoal]",
        "papel": "operador",
        "ativo": True,
    }
    assert (r.conta_id, r.usuario_id, r.origem) == (cenario.locadora.id, cenario.ana.id, "usuario")


def test_listar_so_admin_e_so_da_conta(cenario):
    assert [u.nome for u in cenario.listar.executar(cenario.ctx_admin)] == ["Ana", "Caio"]
    with pytest.raises(AcessoNegado):
        cenario.listar.executar(cenario.ctx_operador)


def test_desativar_usuario(cenario):
    cenario.desativar.executar(cenario.ctx_admin, cenario.operador.id)
    assert cenario.usuarios.obter(cenario.operador.id).ativo is False
    r = cenario.auditoria.registros[-1]
    assert (r.acao, r.entidade, r.entidade_id) == (
        "usuario.desativado",
        "usuario",
        cenario.operador.id,
    )
    assert (r.antes, r.depois) == ({"ativo": True}, {"ativo": False})
    assert (r.conta_id, r.usuario_id) == (cenario.locadora.id, cenario.ana.id)


def test_operador_nao_desativa(cenario):
    with pytest.raises(AcessoNegado):
        cenario.desativar.executar(cenario.ctx_operador, cenario.ana.id)


def test_desativar_a_si_mesmo_falha(cenario):
    with pytest.raises(RegraViolada):
        cenario.desativar.executar(cenario.ctx_admin, cenario.ana.id)


def test_desativar_ultimo_admin_falha(cenario):
    # Ana é a única admin ativa; quem pede é outra pessoa (não é auto-desativação).
    ctx_outro_admin = ContextoConta(cenario.locadora.id, cenario.operador.id, Papel.ADMIN)
    with pytest.raises(RegraViolada):
        cenario.desativar.executar(ctx_outro_admin, cenario.ana.id)
    assert cenario.usuarios.obter(cenario.ana.id).ativo is True


def test_desativar_revoga_sessoes(cenario):
    token = cenario.entrar.executar("caio@locadora.com", SENHA).token
    cenario.desativar.executar(cenario.ctx_admin, cenario.operador.id)
    from motoriz.contas.dominio.sessao import hash_token

    sessao = cenario.sessoes.obter_por_hash_em_todas_as_contas(hash_token(token))
    assert sessao.revogada_em == cenario.relogio.agora()


def test_desativar_usuario_de_outra_conta_e_nao_encontrado(cenario):
    with pytest.raises(NaoEncontrado, match="Usuário não encontrado"):
        cenario.desativar.executar(cenario.ctx_admin, cenario.outro.id)
    assert cenario.banco.usuarios[cenario.outro.id].ativo is True


def test_reativar_usuario(cenario):
    cenario.desativar.executar(cenario.ctx_admin, cenario.operador.id)
    cenario.reativar.executar(cenario.ctx_admin, cenario.operador.id)
    assert cenario.usuarios.obter(cenario.operador.id).ativo is True
    r = cenario.auditoria.registros[-1]
    assert (r.acao, r.entidade_id) == ("usuario.reativado", cenario.operador.id)
    assert (r.antes, r.depois) == ({"ativo": False}, {"ativo": True})


def test_reativar_usuario_de_outra_conta_e_nao_encontrado(cenario):
    with pytest.raises(NaoEncontrado, match="Usuário não encontrado"):
        cenario.reativar.executar(cenario.ctx_admin, cenario.outro.id)


def test_operador_nao_reativa(cenario):
    with pytest.raises(AcessoNegado):
        cenario.reativar.executar(cenario.ctx_operador, cenario.operador.id)


# --- Transições repetidas: sem efeito e sem registro falso na trilha -------------------------


def test_desativar_usuario_ja_inativo_nao_audita(cenario):
    cenario.desativar.executar(cenario.ctx_admin, cenario.operador.id)
    registros = len(cenario.auditoria.registros)
    cenario.desativar.executar(cenario.ctx_admin, cenario.operador.id)
    assert len(cenario.auditoria.registros) == registros
    assert cenario.usuarios.obter(cenario.operador.id).ativo is False


def test_reativar_usuario_ja_ativo_nao_audita(cenario):
    cenario.reativar.executar(cenario.ctx_admin, cenario.operador.id)
    assert cenario.auditoria.registros == []
    assert cenario.usuarios.obter(cenario.operador.id).ativo is True


# --- Regra do último admin sob concorrência ----------------------------------------------------


def test_desativar_bloqueia_a_conta_antes_de_ler(cenario):
    cenario.desativar.executar(cenario.ctx_admin, cenario.operador.id)
    assert cenario.locadoras.bloqueios == [cenario.locadora.id]
