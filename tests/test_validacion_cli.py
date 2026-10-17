"""Pruebas de validación de argumentos en la CLI y manejo de errores sin traceback."""

import pytest

from generador_datos_prueba.cli import main


def test_error_categoria_desconocida(capsys):
    """Verifica que una categoría no válida termine con código no cero y mensaje en stderr."""
    codigo = main(["telefono", "--categoria", "categoria_invalida"])

    captura = capsys.readouterr()
    assert codigo != 0, "Se esperaba código de salida distinto de cero"
    assert "error: categoría desconocida 'categoria_invalida'" in captura.err
    assert "Traceback" not in captura.err


@pytest.mark.parametrize("cantidad_invalida", [0, -1, -10])
def test_error_cantidad_menor_que_uno(capsys, cantidad_invalida):
    """Verifica que --cantidad menor que 1 termine con código no cero y mensaje en stderr."""
    codigo = main(["telefono", "--cantidad", str(cantidad_invalida)])

    captura = capsys.readouterr()
    assert codigo != 0, "Se esperaba código de salida distinto de cero"
    assert f"error: --cantidad ({cantidad_invalida}) debe ser mayor o igual a 1" in captura.err
    assert "Traceback" not in captura.err


@pytest.mark.parametrize("minimo_invalido", [0, -1, -5])
def test_error_min_menor_que_uno(capsys, minimo_invalido):
    """Verifica que --min menor que 1 termine con código no cero y mensaje en stderr."""
    codigo = main(["texto", "--min", str(minimo_invalido)])

    captura = capsys.readouterr()
    assert codigo != 0, "Se esperaba código de salida distinto de cero"
    assert f"error: --min ({minimo_invalido}) no puede ser menor que 1" in captura.err
    assert "Traceback" not in captura.err


def test_error_min_mayor_que_max(capsys):
    """Verifica que --min mayor que --max termine con código no cero y mensaje en stderr."""
    codigo = main(["texto", "--min", "50", "--max", "20"])

    captura = capsys.readouterr()
    assert codigo != 0, "Se esperaba código de salida distinto de cero"
    assert "error: --min (50) no puede ser mayor que --max (20)" in captura.err
    assert "Traceback" not in captura.err


def test_error_archivo_salida_no_escribible(capsys, tmp_path):
    """Verifica que una falla de OSError al escribir el archivo termine con código no cero sin traceback."""
    # En cualquier SO, intentar abrir un directorio existente en modo 'w' levanta OSError (IsADirectoryError o PermissionError)
    directorio_como_archivo = tmp_path / "directorio_existente"
    directorio_como_archivo.mkdir()

    codigo = main(["texto", "--salida", str(directorio_como_archivo)])

    captura = capsys.readouterr()
    assert codigo != 0, "Se esperaba código de salida distinto de cero"
    assert "error: no se pudo escribir en el archivo de salida" in captura.err
    assert str(directorio_como_archivo) in captura.err
    assert "Traceback" not in captura.err
