class ErroDeDominio(Exception):
    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class NaoEncontrado(ErroDeDominio):
    pass


class AcessoNegado(ErroDeDominio):
    pass


class Conflito(ErroDeDominio):
    pass


class RegraViolada(ErroDeDominio):
    pass
