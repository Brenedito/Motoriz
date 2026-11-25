from motoriz.compartilhado.erros import Conflito, ErroDeDominio


class CredenciaisInvalidas(ErroDeDominio):
    def __init__(self, mensagem: str = "E-mail ou senha incorretos.") -> None:
        super().__init__(mensagem)


class SessaoInvalida(ErroDeDominio):
    def __init__(self, mensagem: str = "Sessão expirada. Entre novamente.") -> None:
        super().__init__(mensagem)


class SenhaAtualIncorreta(ErroDeDominio):
    """Ao trocar a senha. Não é `CredenciaisInvalidas`: a sessão segue válida (422, não 401)."""

    def __init__(self, mensagem: str = "Senha atual incorreta.") -> None:
        super().__init__(mensagem)


class SenhaFraca(ErroDeDominio):
    pass


class LocadoraJaCadastrada(Conflito):
    def __init__(self, mensagem: str = "Já existe uma locadora com este documento") -> None:
        super().__init__(mensagem)


class EmailJaCadastrado(Conflito):
    def __init__(self, mensagem: str = "Já existe um usuário com este e-mail") -> None:
        super().__init__(mensagem)
