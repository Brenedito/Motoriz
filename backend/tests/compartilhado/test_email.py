import pytest

from motoriz.compartilhado.email import Email, EmailInvalido


def test_email_normaliza_espacos_e_maiusculas() -> None:
    assert Email.de("  Ana@Locadora.COM ").valor == "ana@locadora.com"


@pytest.mark.parametrize(
    "texto",
    [
        "ana",
        "ana@",
        "@locadora.com",
        "ana@locadora",
        "a@@b.com",
        "ana maria@locadora.com",
        "ana@loca dora.com",
        "ana@locadora..com",
        "ana@.locadora.com",
        "a" * 64 + "@" + "b" * 186 + ".com",
    ],
)
def test_email_invalido(texto: str) -> None:
    with pytest.raises(EmailInvalido) as erro:
        Email.de(texto)
    assert erro.value.mensagem == "E-mail inválido"
