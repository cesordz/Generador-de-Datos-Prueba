"""Generador de datos de prueba para nombres de personas."""

import json
from pathlib import Path
import random
import sys


# Para este generador, un nombre se considera "válido" si contiene caracteres
# alfabéticos válidos (incluyendo acentos, ñ, diéresis, apóstrofos o guiones legítimos),
# no contiene código hostil ni símbolos arbitrarios, y su longitud en caracteres se
# encuentra dentro del rango permitido [minimo, maximo].


def _cargar_datos() -> tuple[list[str], list[str]]:
    """Carga los nombres y apellidos hispanos desde el archivo de datos JSON."""
    ruta_json = Path(__file__).resolve().parent.parent / "datos" / "nombres.json"
    if ruta_json.exists():
        with open(ruta_json, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("nombres", []), data.get("apellidos", [])
    return ["Sofía", "Mateo"], ["Rodríguez", "González"]


def _generar_cadena_alfabetica(rng: random.Random, longitud: int) -> str:
    """Genera una cadena alfabética capitalizada de longitud exacta usando rng."""
    if longitud <= 0:
        return ""
    alfabeto = "abcdefghijklmnopqrstuvwxyz"
    letras = [rng.choice(alfabeto) for _ in range(longitud)]
    letras[0] = letras[0].upper()
    return "".join(letras)


def _obtener_casos_invalidos(minimo: int) -> list[tuple[str, str]]:
    """Devuelve los casos de prueba inválidos para nombres."""
    casos = [
        ("", "cadena vacía no permitida para nombre"),
        ("123456", "contiene exclusivamente dígitos numéricos"),
        ("@#$%^&*", "contiene símbolos y caracteres especiales no permitidos"),
    ]
    if minimo >= 2:
        casos.append(("A", f"longitud 1 inferior al mínimo permitido ({minimo})"))
    return casos


def _obtener_casos_hostiles() -> list[tuple[str, bool, str]]:
    """Devuelve los casos hostiles y especifica si un sistema razonable debe aceptarlos."""
    return [
        ("   ", False, "cadena compuesta exclusivamente por espacios en blanco"),
        ("O'Brien", True, "nombre con apóstrofo legítimo de origen gaélico que un sistema razonable debe aceptar"),
        ("María-José", True, "nombre compuesto con guion legítimo que un sistema razonable debe aceptar"),
        ("Muñoz Güemes", True, "nombre con caracteres legítimos del español (ñ y diéresis) que un sistema razonable debe aceptar"),
        ("Александр", False, "contiene caracteres de un alfabeto no latino (cirílico)"),
        ("Carlos 😀", False, "contiene caracteres emoji no permitidos"),
        ("Juan  Pérez", False, "contiene espacios dobles consecutivos sin normalizar"),
        (" Ana Gómez ", False, "contiene espacios en blanco al inicio y al final"),
        ("<script>alert(1)</script>", False, "intento de inyección de script HTML (XSS)"),
        ("Carlos' OR 1=1 --", False, "intento de inyección de código SQL"),
    ]


def generar(
    categoria: str,
    cantidad: int | None,
    rng: random.Random,
    minimo: int = 2,
    maximo: int = 50,
) -> list[dict]:
    """Genera registros de datos de prueba para el campo nombre."""
    registros: list[dict] = []

    if categoria == "validos":
        nombres, apellidos = _cargar_datos()
        total = 10 if cantidad is None else cantidad
        for _ in range(total):
            nombre_elegido = rng.choice(nombres)
            apellido_elegido = rng.choice(apellidos)
            valor = f"{nombre_elegido} {apellido_elegido}"
            longitud = len(valor)
            registros.append(
                {
                    "campo": "nombre",
                    "valor": valor,
                    "categoria": "validos",
                    "valido": True,
                    "motivo": f"nombre hispano válido de longitud {longitud} dentro del rango permitido [{minimo}, {maximo}]",
                }
            )

    elif categoria == "invalidos":
        casos = _obtener_casos_invalidos(minimo)
        total = len(casos) if cantidad is None else cantidad
        for i in range(total):
            valor, motivo = casos[i % len(casos)]
            registros.append(
                {
                    "campo": "nombre",
                    "valor": valor,
                    "categoria": "invalidos",
                    "valido": False,
                    "motivo": motivo,
                }
            )

    elif categoria == "limite":
        if cantidad is not None:
            sys.stderr.write("aviso: --cantidad no aplica para la categoría 'limite' y se ignora.\n")

        candidatos = [
            minimo - 1,
            minimo,
            minimo + 1,
            maximo - 1,
            maximo,
            maximo + 1,
        ]

        longitudes: list[int] = []
        for l in candidatos:
            if l >= 0 and l not in longitudes:
                longitudes.append(l)

        for longitud in longitudes:
            valor = _generar_cadena_alfabetica(rng, longitud)
            es_valido = minimo <= longitud <= maximo
            if es_valido:
                motivo = f"longitud {longitud} dentro del rango permitido [{minimo}, {maximo}]"
            else:
                motivo = f"longitud {longitud} fuera del rango permitido [{minimo}, {maximo}]"

            registros.append(
                {
                    "campo": "nombre",
                    "valor": valor,
                    "categoria": "limite",
                    "valido": es_valido,
                    "motivo": motivo,
                }
            )

    elif categoria == "hostiles":
        casos = _obtener_casos_hostiles()
        total = len(casos) if cantidad is None else cantidad
        for i in range(total):
            valor, valido, motivo = casos[i % len(casos)]
            registros.append(
                {
                    "campo": "nombre",
                    "valor": valor,
                    "categoria": "hostiles",
                    "valido": valido,
                    "motivo": motivo,
                }
            )

    return registros
