import pytest

from motoriz.compartilhado.contexto import Papel
from motoriz.compartilhado.documento import DocumentoInvalido
from motoriz.compartilhado.erros import NaoEncontrado
from motoriz.contas.dominio.erros import EmailJaCadastrado, LocadoraJaCadastrada
from motoriz.contas.dominio.locadora import SituacaoLocadora

DOC = "11.222.333/0001-81"


def _criar(cenario, documento=DOC, email="ana@x.com"):
    return cenario.criar_locadora.executar("Loca Sul", documento, "(51) 9999", "Ana", email)


def test_criar_locadora_cria_admin_ativo(cenario_vazio):
    r = _criar(cenario_vazio)
    assert r.admin.papel is Papel.ADMIN and r.admin.ativo and len(r.senha_inicial) == 16
    assert r.admin.conta_id == r.locadora.id
    assert [x.acao for x in cenario_vazio.auditoria.registros] == [
        "locadora.criada",
        "usuario.criado",
    ]


def test_criar_locadora_grava_locadora_e_admin(cenario_vazio):
    r = _criar(cenario_vazio, email=" ANA@x.com ")
    assert cenario_vazio.locadoras.obter(r.locadora.id) == r.locadora
    assert r.locadora.documento.valor == "11222333000181"
    assert r.locadora.situacao is SituacaoLocadora.ATIVA
    assert r.admin.email.valor == "ana@x.com"
    assert r.admin.hash_senha == "hash:" + r.senha_inicial


def test_criar_locadora_audita_como_suporte(cenario_vazio):
    r = _criar(cenario_vazio)
    criada, usuario = cenario_vazio.auditoria.registros
    for reg in (criada, usuario):
        assert (reg.conta_id, reg.usuario_id, reg.origem) == (r.locadora.id, None, "suporte")
    assert (criada.entidade, criada.entidade_id) == ("locadora", r.locadora.id)
    assert criada.depois == {
        "nome": "Loca Sul",
        "documento": "11222333000181",
        "contato": "[dado pessoal]",
        "situacao": "ativa",
    }
    assert (usuario.entidade, usuario.entidade_id) == ("usuario", r.admin.id)
    assert usuario.depois == {
        "nome": "[dado pessoal]",
        "email": "[dado pessoal]",
        "papel": "admin",
        "ativo": True,
    }
    assert r.senha_inicial not in repr(cenario_vazio.auditoria.registros)


def test_senhas_iniciais_diferem(cenario_vazio):
    a = _criar(cenario_vazio)
    b = _criar(cenario_vazio, documento="11.444.777/0001-61", email="b@x.com")
    assert a.senha_inicial != b.senha_inicial


def test_documento_duplicado(cenario_vazio):
    _criar(cenario_vazio)
    with pytest.raises(LocadoraJaCadastrada, match="Já existe uma locadora com este documento"):
        _criar(cenario_vazio, email="outra@x.com")


def test_email_duplicado_nao_deixa_locadora_gravada(cenario_vazio):
    _criar(cenario_vazio)
    with pytest.raises(EmailJaCadastrado):
        _criar(cenario_vazio, documento="11.444.777/0001-61")
    assert len(cenario_vazio.banco.locadoras) == 1


def test_documento_invalido(cenario_vazio):
    with pytest.raises(DocumentoInvalido):
        _criar(cenario_vazio, documento="123")


def test_suspender_e_reativar_locadora(cenario_vazio):
    r = _criar(cenario_vazio)
    cenario_vazio.suspender.executar(DOC)
    assert cenario_vazio.locadoras.obter(r.locadora.id).situacao is SituacaoLocadora.SUSPENSA
    s = cenario_vazio.auditoria.registros[-1]
    assert (s.acao, s.entidade, s.entidade_id) == ("locadora.suspensa", "locadora", r.locadora.id)
    assert (s.conta_id, s.usuario_id, s.origem) == (r.locadora.id, None, "suporte")
    cenario_vazio.reativar.executar(DOC)
    assert cenario_vazio.locadoras.obter(r.locadora.id).situacao is SituacaoLocadora.ATIVA
    assert cenario_vazio.auditoria.registros[-1].acao == "locadora.reativada"


def test_suspender_locadora_inexistente(cenario_vazio):
    with pytest.raises(NaoEncontrado, match="Locadora não encontrada"):
        cenario_vazio.suspender.executar(DOC)


def test_reativar_locadora_inexistente(cenario_vazio):
    with pytest.raises(NaoEncontrado, match="Locadora não encontrada"):
        cenario_vazio.reativar.executar(DOC)


# --- Transições repetidas: sem efeito e sem registro falso na trilha -------------------------


def test_suspender_locadora_ja_suspensa_nao_audita(cenario_vazio):
    r = _criar(cenario_vazio)
    cenario_vazio.suspender.executar(DOC)
    registros = len(cenario_vazio.auditoria.registros)
    cenario_vazio.suspender.executar(DOC)
    assert len(cenario_vazio.auditoria.registros) == registros
    assert cenario_vazio.locadoras.obter(r.locadora.id).situacao is SituacaoLocadora.SUSPENSA


def test_reativar_locadora_ja_ativa_nao_audita(cenario_vazio):
    _criar(cenario_vazio)
    registros = len(cenario_vazio.auditoria.registros)
    cenario_vazio.reativar.executar(DOC)
    assert len(cenario_vazio.auditoria.registros) == registros


def test_suspender_e_reativar_auditam_a_situacao_real(cenario_vazio):
    _criar(cenario_vazio)
    cenario_vazio.suspender.executar(DOC)
    s = cenario_vazio.auditoria.registros[-1]
    assert (s.antes, s.depois) == ({"situacao": "ativa"}, {"situacao": "suspensa"})
    cenario_vazio.reativar.executar(DOC)
    r = cenario_vazio.auditoria.registros[-1]
    assert (r.antes, r.depois) == ({"situacao": "suspensa"}, {"situacao": "ativa"})


# --- Dado pessoal na trilha da locadora --------------------------------------------------------


def test_locadora_pessoa_fisica_audita_sem_dado_pessoal(cenario_vazio):
    r = _criar(cenario_vazio, documento="529.982.247-25")
    criada = cenario_vazio.auditoria.registros[0]
    assert criada.acao == "locadora.criada"
    assert criada.depois == {
        "nome": "[dado pessoal]",
        "documento": "[dado pessoal]",
        "contato": "[dado pessoal]",
        "situacao": "ativa",
    }
    assert r.locadora.documento.valor not in repr(cenario_vazio.auditoria.registros)


def test_locadora_pessoa_juridica_mascara_so_o_contato(cenario_vazio):
    _criar(cenario_vazio)
    criada = cenario_vazio.auditoria.registros[0]
    assert criada.depois == {
        "nome": "Loca Sul",
        "documento": "11222333000181",
        "contato": "[dado pessoal]",
        "situacao": "ativa",
    }
