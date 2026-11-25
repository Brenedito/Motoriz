"""CLI do suporte: cria, suspende e reativa locadoras (`motoriz-suporte`)."""

import argparse
import sys

from sqlalchemy.orm import Session

from motoriz.auditoria.api import RegistradorSql
from motoriz.compartilhado.erros import ErroDeDominio
from motoriz.compartilhado.relogio import RelogioDoSistema
from motoriz.contas.adaptadores.hasher_argon2 import HasherArgon2
from motoriz.contas.adaptadores.repositorios import RepositorioLocadorasSql, RepositorioUsuariosSql
from motoriz.contas.aplicacao.suporte import CriarLocadora, ReativarLocadora, SuspenderLocadora
from motoriz.infra.banco import criar_fabrica, criar_motor
from motoriz.infra.config import obter_configuracao
from motoriz.infra.conta import modo_plataforma


def _criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="motoriz-suporte", description="Ferramentas do suporte da Motoriz."
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    criar = sub.add_parser("criar-locadora", help="Cria uma locadora e o seu administrador.")
    criar.add_argument("--nome", required=True)
    criar.add_argument("--documento", required=True, help="CNPJ ou CPF")
    criar.add_argument("--contato", required=True)
    criar.add_argument("--admin-nome", required=True)
    criar.add_argument("--admin-email", required=True)

    for nome, ajuda in (
        ("suspender-locadora", "Suspende a locadora e derruba as sessões abertas."),
        ("reativar-locadora", "Reativa uma locadora suspensa."),
    ):
        comando = sub.add_parser(nome, help=ajuda)
        comando.add_argument("--documento", required=True, help="CNPJ ou CPF")
    return parser


def _executar(args: argparse.Namespace, sessao: Session) -> None:
    relogio = RelogioDoSistema()
    locadoras = RepositorioLocadorasSql(sessao, relogio)
    auditoria = RegistradorSql(sessao, relogio)
    if args.comando == "criar-locadora":
        criada = CriarLocadora(
            locadoras=locadoras,
            usuarios=RepositorioUsuariosSql(sessao, relogio),
            hasher=HasherArgon2(),
            auditoria=auditoria,
        ).executar(args.nome, args.documento, args.contato, args.admin_nome, args.admin_email)
        print(f"Locadora criada: {criada.locadora.nome}")
        print(f"Admin: {criada.admin.email.valor}")
        print(f"Senha inicial: {criada.senha_inicial}")
        print("Troque a senha no primeiro acesso.")
    elif args.comando == "suspender-locadora":
        SuspenderLocadora(locadoras=locadoras, auditoria=auditoria).executar(args.documento)
    else:
        ReativarLocadora(locadoras=locadoras, auditoria=auditoria).executar(args.documento)


def main(argv: list[str] | None = None) -> int:
    args = _criar_parser().parse_args(argv)
    motor = criar_motor(obter_configuracao().url_banco_app)
    try:
        with criar_fabrica(motor)() as sessao:
            modo_plataforma(sessao)
            try:
                _executar(args, sessao)
                sessao.commit()
            except ErroDeDominio as erro:
                sessao.rollback()
                print(f"Erro: {erro.mensagem}", file=sys.stderr)
                return 1
            except Exception:
                sessao.rollback()
                raise
    finally:
        motor.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
