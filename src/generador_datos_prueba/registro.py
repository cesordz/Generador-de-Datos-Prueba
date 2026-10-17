from typing import TypedDict


class Registro(TypedDict):
    """Representa un registro de dato de prueba generado."""

    campo: str
    valor: str
    categoria: str
    valido: bool
    motivo: str
