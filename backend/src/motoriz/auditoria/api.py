"""Superfície pública do módulo de auditoria: outros módulos importam só daqui."""

from motoriz.auditoria.adaptadores.registrador_sql import RegistradorSql
from motoriz.auditoria.aplicacao.consultar import ConsultarTrilha
from motoriz.auditoria.aplicacao.portas import RegistradorDeAcoes
from motoriz.auditoria.dominio.registro import MARCADOR_PESSOAL, RegistroDeAcao

__all__ = [
    "MARCADOR_PESSOAL",
    "ConsultarTrilha",
    "RegistradorDeAcoes",
    "RegistradorSql",
    "RegistroDeAcao",
]
