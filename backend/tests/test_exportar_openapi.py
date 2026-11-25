import json
import os
import subprocess
import sys

from fastapi import FastAPI


def test_exporta_openapi_sem_banco_nem_configuracao(tmp_path):
    # Sem variáveis MOTORIZ_ e fora de backend/ (sem .env): criar o app não pode exigir banco.
    ambiente = {k: v for k, v in os.environ.items() if not k.startswith("MOTORIZ_")}
    saida = subprocess.run(
        [sys.executable, "-m", "motoriz.exportar_openapi"],
        capture_output=True,
        check=True,
        cwd=tmp_path,
        env=ambiente,
    )
    esquema = json.loads(saida.stdout.decode("utf-8"))
    assert "/api/sessao" in esquema["paths"]
    assert "/api/usuarios/{id}/desativar" in esquema["paths"]
    assert "/api/auditoria" in esquema["paths"]


def test_modulo_app_expoe_app_para_fastapi_dev():
    from motoriz import app as modulo

    assert isinstance(modulo.app, FastAPI)
