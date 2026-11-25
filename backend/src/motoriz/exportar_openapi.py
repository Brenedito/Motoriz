"""Imprime o esquema OpenAPI da API em JSON, sem precisar de banco.

Uso: `uv run python -m motoriz.exportar_openapi > openapi.json`
"""

import json
import sys

from motoriz.app import criar_app


def main() -> None:
    # UTF-8 sempre: no Windows a saída redirecionada usaria a página de código do sistema.
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    json.dump(criar_app().openapi(), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
