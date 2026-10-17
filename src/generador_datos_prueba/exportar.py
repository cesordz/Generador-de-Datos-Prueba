import csv
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import TextIO

from generador_datos_prueba.registro import Registro

CAMPOS_REGISTRO: list[str] = ["campo", "valor", "categoria", "valido", "motivo"]


def _asegurar_stdout_utf8() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


def exportar_json(
    registros: Iterable[Registro],
    salida: str | Path | TextIO | None = None,
) -> None:
    """Exporta los registros en formato JSON a stdout o al archivo especificado."""
    lista = list(registros)
    contenido = json.dumps(lista, indent=2, ensure_ascii=False) + "\n"

    if salida is None or salida == "-":
        _asegurar_stdout_utf8()
        sys.stdout.write(contenido)
    elif isinstance(salida, (str, Path)):
        with open(salida, mode="w", encoding="utf-8") as f:
            f.write(contenido)
    else:
        salida.write(contenido)


def exportar_csv(
    registros: Iterable[Registro],
    salida: str | Path | TextIO | None = None,
) -> None:
    """Exporta los registros en formato CSV a stdout o al archivo especificado."""
    if salida is None or salida == "-":
        _asegurar_stdout_utf8()
        writer = csv.DictWriter(sys.stdout, fieldnames=CAMPOS_REGISTRO, lineterminator="\n")
        writer.writeheader()
        writer.writerows(registros)
    elif isinstance(salida, (str, Path)):
        with open(salida, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_REGISTRO, lineterminator="\n")
            writer.writeheader()
            writer.writerows(registros)
    else:
        writer = csv.DictWriter(salida, fieldnames=CAMPOS_REGISTRO, lineterminator="\n")
        writer.writeheader()
        writer.writerows(registros)
