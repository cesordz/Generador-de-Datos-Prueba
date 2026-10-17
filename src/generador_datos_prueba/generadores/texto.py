"""Generador de datos de prueba para cadenas de texto."""

import json
from pathlib import Path
import random
import sys


# Para este generador, un texto se considera "válido" si contiene caracteres
# alfanuméricos y signos de puntuación comunes que forman frases legibles, no
# consiste únicamente en espacios en blanco ni código malicioso, y su longitud en
# caracteres está dentro del rango permitido [minimo, maximo].


FRASES_VALIDAS = [
    "El acceso al sistema fue concedido correctamente.",
    "Datos guardados de forma segura en la base de datos.",
    "La consulta se completó en un tiempo aceptable.",
    "Operación completada sin errores detectados.",
    "Configuración de usuario actualizada recientemente.",
    "El documento ha sido firmado digitalmente.",
    "Verificación de integridad finalizada con éxito.",
    "Se ha enviado un correo de confirmación al usuario.",
    "Registro procesado y validado satisfactoriamente.",
    "El informe mensual se ha generado con los datos solicitados.",
]


def _cargar_hostiles() -> list[dict]:
    """Carga la lista de cadenas hostiles desde el archivo de datos JSON."""
    ruta_json = Path(__file__).resolve().parent.parent / "datos" / "hostiles.json"
    if ruta_json.exists():
        with open(ruta_json, mode="r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"valor": "<script>alert(1)</script>", "motivo": "inyección de script HTML (XSS)"},
        {"valor": "' OR 1=1; --", "motivo": "inyección de código SQL"},
    ]


def _generar_cadena_longitud(rng: random.Random, longitud: int) -> str:
    """Genera una cadena de texto de la longitud exacta usando rng."""
    if longitud <= 0:
        return ""
    alfabeto = "abcdefghijklmnopqrstuvwxyz"
    letras = [rng.choice(alfabeto) for _ in range(longitud)]
    letras[0] = letras[0].upper()
    return "".join(letras)


def generar(
    categoria: str,
    cantidad: int | None,
    rng: random.Random,
    minimo: int = 1,
    maximo: int = 255,
) -> list[dict]:
    """Genera registros de datos de prueba para el campo texto."""
    registros: list[dict] = []

    if categoria == "validos":
        total = 10 if cantidad is None else cantidad
        for _ in range(total):
            frase = rng.choice(FRASES_VALIDAS)
            # Asegurar que esté dentro del rango permitido si la frase original excede maximo
            if len(frase) > maximo:
                frase = frase[:maximo]
            elif len(frase) < minimo:
                frase = frase.ljust(minimo, ".")
            longitud = len(frase)
            registros.append(
                {
                    "campo": "texto",
                    "valor": frase,
                    "categoria": "validos",
                    "valido": True,
                    "motivo": f"frase válida de longitud {longitud} dentro del rango permitido [{minimo}, {maximo}]",
                }
            )

    elif categoria == "invalidos":
        casos = [
            ("", "cadena de texto vacía no permitida"),
            ("     ", "cadena de texto compuesta exclusivamente por espacios en blanco"),
        ]
        total = len(casos) if cantidad is None else cantidad
        for i in range(total):
            valor, motivo = casos[i % len(casos)]
            registros.append(
                {
                    "campo": "texto",
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
            valor = _generar_cadena_longitud(rng, longitud)
            es_valido = minimo <= longitud <= maximo
            if es_valido:
                motivo = f"longitud {longitud} dentro del rango permitido [{minimo}, {maximo}]"
            else:
                motivo = f"longitud {longitud} fuera del rango permitido [{minimo}, {maximo}]"

            registros.append(
                {
                    "campo": "texto",
                    "valor": valor,
                    "categoria": "limite",
                    "valido": es_valido,
                    "motivo": motivo,
                }
            )

    elif categoria == "hostiles":
        casos = _cargar_hostiles()
        total = len(casos) if cantidad is None else cantidad
        for i in range(total):
            item = casos[i % len(casos)]
            registros.append(
                {
                    "campo": "texto",
                    "valor": item["valor"],
                    "categoria": "hostiles",
                    "valido": False,
                    "motivo": item["motivo"],
                }
            )

    return registros
