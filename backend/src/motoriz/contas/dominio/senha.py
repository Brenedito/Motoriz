from motoriz.contas.dominio.erros import SenhaFraca

TAMANHO_MINIMO = 10
TAMANHO_MAXIMO = 128


def validar_senha(senha: str) -> None:
    if not TAMANHO_MINIMO <= len(senha) <= TAMANHO_MAXIMO:
        raise SenhaFraca(
            f"A senha deve ter entre {TAMANHO_MINIMO} e {TAMANHO_MAXIMO} caracteres"
        )
