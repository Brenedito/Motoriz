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
