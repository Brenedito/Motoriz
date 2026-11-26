from motoriz.compartilhado.erros import ErroDeDominio


class TextoInvalido(ErroDeDominio):
    pass


def texto_obrigatorio(valor: str, *, campo: str, maximo: int) -> str:
    """Apara o texto e exige que não fique vazio nem passe do tamanho da coluna.

    Sem o limite aqui, o texto longo chega ao MySQL e vira DataError (500) em vez de 422.
    """
    aparado = valor.strip()
    if not aparado:
        raise TextoInvalido(f"Informe o {campo}")
    if len(aparado) > maximo:
        raise TextoInvalido(f"O {campo} deve ter no máximo {maximo} caracteres")
    return aparado
