"""Pruebas de reproducibilidad con semilla para los cuatro subcomandos."""

import random
import pytest

from generador_datos_prueba.generadores import email, nombre, telefono, texto

GENERADORES = [
    ("telefono", telefono.generar),
    ("email", email.generar),
    ("nombre", nombre.generar),
    ("texto", texto.generar),
]


@pytest.mark.parametrize("nombre_campo, funcion_generar", GENERADORES)
def test_misma_semilla_produce_salida_identica(nombre_campo, funcion_generar):
    """Verifica que dos ejecuciones con la misma semilla generen exactamente la misma secuencia."""
    semilla = 42
    rng_a = random.Random(semilla)
    rng_b = random.Random(semilla)

    registros_a = funcion_generar(categoria="validos", cantidad=10, rng=rng_a)
    registros_b = funcion_generar(categoria="validos", cantidad=10, rng=rng_b)

    assert len(registros_a) == 10
    assert registros_a == registros_b, f"La misma semilla generó datos distintos en {nombre_campo}"


@pytest.mark.parametrize("nombre_campo, funcion_generar", GENERADORES)
def test_semillas_distintas_producen_salidas_distintas(nombre_campo, funcion_generar):
    """Verifica que dos ejecuciones con semillas diferentes generen secuencias distintas."""
    rng_a = random.Random(1001)
    rng_b = random.Random(9999)

    registros_a = funcion_generar(categoria="validos", cantidad=10, rng=rng_a)
    registros_b = funcion_generar(categoria="validos", cantidad=10, rng=rng_b)

    assert registros_a != registros_b, f"Semillas distintas produjeron datos idénticos en {nombre_campo}"
