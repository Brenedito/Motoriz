import pytest

from motoriz.contas.dominio.erros import SenhaFraca
from motoriz.contas.dominio.senha import validar_senha


@pytest.mark.parametrize("senha", ["curta", "x" * 129])
def test_senha_fora_do_limite(senha):
    with pytest.raises(SenhaFraca, match="entre 10 e 128"):
        validar_senha(senha)


@pytest.mark.parametrize("senha", ["x" * 10, "x" * 128, "çãoáéíóú🚗🚗", "senha com espaço"])
def test_senha_aceita(senha):
    validar_senha(senha)
