from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy.dialects import mysql

from motoriz.infra.tipos import DataHoraUTC

DIALETO = mysql.dialect()


def test_grava_em_utc_sem_fuso():
    brasilia = timezone(timedelta(hours=-3))
    valor = datetime(2026, 11, 24, 9, 0, 0, 5, tzinfo=brasilia)
    assert DataHoraUTC().process_bind_param(valor, DIALETO) == datetime(2026, 11, 24, 12, 0, 0, 5)


def test_recusa_datetime_sem_fuso():
    with pytest.raises(ValueError):
        DataHoraUTC().process_bind_param(datetime(2026, 11, 24), DIALETO)


def test_le_com_fuso_utc():
    lido = DataHoraUTC().process_result_value(datetime(2026, 11, 24, 12), DIALETO)
    assert lido == datetime(2026, 11, 24, 12, tzinfo=UTC)
    assert lido.tzinfo is UTC
