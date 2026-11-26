import pytest

from motoriz.compartilhado.documento import Documento, DocumentoInvalido


def test_cpf_valido_com_mascara() -> None:
    d = Documento.de("529.982.247-25")
    assert (d.valor, d.tipo) == ("52998224725", "CPF")


def test_cnpj_valido_com_mascara() -> None:
    d = Documento.de("11.222.333/0001-81")
    assert (d.valor, d.tipo) == ("11222333000181", "CNPJ")


@pytest.mark.parametrize(
    "texto", ["529.982.247-26", "111.111.111-11", "11.222.333/0001-80", "123", ""]
)
def test_documento_invalido(texto: str) -> None:
    with pytest.raises(DocumentoInvalido) as erro:
        Documento.de(texto)
    assert erro.value.mensagem == "CPF ou CNPJ inválido"


def test_cnpj_alfanumerico_valido() -> None:
    # Exemplo oficial da Receita Federal (CNPJ alfanumérico, emitido a partir de julho de 2026).
    d = Documento.de("12.ABC.345/01DE-35")
    assert (d.valor, d.tipo) == ("12ABC34501DE35", "CNPJ")


def test_cnpj_alfanumerico_aceita_minusculas() -> None:
    assert Documento.de("12.abc.345/01de-35").valor == "12ABC34501DE35"


@pytest.mark.parametrize(
    "texto",
    [
        "12.ABC.345/01DE-36",  # dígito verificador errado
        "12.ABC.345/01DE-3A",  # dígito verificador tem de ser número
        "529.982.247-2A",  # CPF não tem letras
        "12ÁBC34501DE35",  # só letras A-Z
    ],
)
def test_cnpj_alfanumerico_invalido(texto: str) -> None:
    with pytest.raises(DocumentoInvalido):
        Documento.de(texto)
