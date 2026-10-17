"""Generador de datos de prueba para números de teléfono."""

import random
import sys


# Para este generador, un número de teléfono se considera "válido" si contiene
# exclusivamente dígitos numéricos, su longitud está dentro del rango permitido
# [minimo, maximo] y no comienza con el dígito '0'.


def _generar_cadena_digitos(rng: random.Random, longitud: int) -> str:
    """Genera una cadena de dígitos de la longitud especificada usando rng."""
    if longitud <= 0:
        return ""
    if longitud == 1:
        return str(rng.randint(1, 9))
    primer_digito = str(rng.randint(1, 9))
    resto = "".join(str(rng.randint(0, 9)) for _ in range(longitud - 1))
    return primer_digito + resto


def generar(
    categoria: str,
    cantidad: int | None,
    rng: random.Random,
    minimo: int = 10,
    maximo: int = 10,
) -> list[dict]:
    """Genera registros de datos de prueba para el campo teléfono."""
    registros: list[dict] = []

    if categoria == "validos":
        total = 10 if cantidad is None else cantidad
        for _ in range(total):
            longitud = rng.randint(minimo, maximo)
            valor = _generar_cadena_digitos(rng, longitud)
            registros.append(
                {
                    "campo": "telefono",
                    "valor": valor,
                    "categoria": "validos",
                    "valido": True,
                    "motivo": f"longitud {longitud} dentro del rango permitido [{minimo}, {maximo}]",
                }
            )

    elif categoria == "limite":
        if cantidad is not None:
            sys.stderr.write("aviso: --cantidad no aplica para la categoría 'limite' y se ignora.\n")

        # Candidatos de longitud límite: minimo-1, minimo, minimo+1, maximo-1, maximo, maximo+1
        candidatos = [
            minimo - 1,
            minimo,
            minimo + 1,
            maximo - 1,
            maximo,
            maximo + 1,
        ]

        # Sin duplicados manteniendo el orden y excluyendo longitudes negativas
        longitudes: list[int] = []
        for l in candidatos:
            if l >= 0 and l not in longitudes:
                longitudes.append(l)

        for longitud in longitudes:
            valor = _generar_cadena_digitos(rng, longitud)
            es_valido = minimo <= longitud <= maximo
            if es_valido:
                motivo = f"longitud {longitud} dentro del rango permitido [{minimo}, {maximo}]"
            else:
                motivo = f"longitud {longitud} fuera del rango permitido [{minimo}, {maximo}]"

            registros.append(
                {
                    "campo": "telefono",
                    "valor": valor,
                    "categoria": "limite",
                    "valido": es_valido,
                    "motivo": motivo,
                }
            )

    return registros
