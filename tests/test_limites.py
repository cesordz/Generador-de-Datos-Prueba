"""Pruebas de comportamiento para casos límite."""

import random
import pytest

from generador_datos_prueba.generadores import email, nombre, telefono, texto

GENERADORES_CON_RANGO = [
    ("telefono", telefono.generar),
    ("nombre", nombre.generar),
    ("texto", texto.generar),
]


@pytest.mark.parametrize("nombre_campo, funcion_generar", GENERADORES_CON_RANGO)
def test_limites_min_3_max_8_producen_longitudes_exactas(nombre_campo, funcion_generar):
    """Verifica que con --min 3 y --max 8 se generen exactamente las longitudes 2, 3, 4, 7, 8 y 9."""
    rng = random.Random(1)
    registros = funcion_generar(
        categoria="limite",
        cantidad=None,
        rng=rng,
        minimo=3,
        maximo=8,
    )

    longitudes = [len(reg["valor"]) for reg in registros]
    esperadas = [2, 3, 4, 7, 8, 9]

    assert longitudes == esperadas, (
        f"En {nombre_campo} con min=3 y max=8 se esperaban longitudes {esperadas}, pero se obtuvo {longitudes}"
    )


@pytest.mark.parametrize("nombre_campo, funcion_generar", GENERADORES_CON_RANGO)
def test_limites_min_1_max_1_sin_duplicados(nombre_campo, funcion_generar):
    """Verifica que con --min 1 y --max 1 no existan valores ni longitudes duplicadas."""
    rng = random.Random(1)
    registros = funcion_generar(
        categoria="limite",
        cantidad=None,
        rng=rng,
        minimo=1,
        maximo=1,
    )

    longitudes = [len(reg["valor"]) for reg in registros]
    valores = [reg["valor"] for reg in registros]

    # Con min=1 y max=1 las longitudes válidas son [0, 1, 2]
    assert longitudes == [0, 1, 2], f"En {nombre_campo} las longitudes no coinciden con [0, 1, 2]"
    assert len(longitudes) == len(set(longitudes)), f"Se detectaron longitudes duplicadas en {nombre_campo}"
    assert len(valores) == len(set(valores)), f"Se detectaron valores duplicados en {nombre_campo}"


def test_email_limite_tiene_usuarios_de_64_y_65():
    """Verifica que en email límite existan usuarios con longitud de 64 y 65 caracteres."""
    rng = random.Random(1)
    registros = email.generar(categoria="limite", cantidad=None, rng=rng)

    usuarios_longitudes = {}
    for reg in registros:
        valor = reg["valor"]
        if "@" in valor:
            usuario = valor.split("@")[0]
            usuarios_longitudes[len(usuario)] = reg

    assert 64 in usuarios_longitudes, "No se encontró caso límite con usuario de 64 caracteres"
    assert 65 in usuarios_longitudes, "No se encontró caso límite con usuario de 65 caracteres"

    assert usuarios_longitudes[64]["valido"] is True, "El usuario de 64 caracteres debe ser válido (límite RFC 5321)"
    assert usuarios_longitudes[65]["valido"] is False, "El usuario de 65 caracteres debe ser inválido (excede RFC 5321)"
