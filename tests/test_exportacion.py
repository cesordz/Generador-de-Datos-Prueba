"""Pruebas de exportación a formatos CSV y JSON."""

import csv
import io
import json
import pytest

from generador_datos_prueba.exportar import CAMPOS_REGISTRO, exportar_csv, exportar_json
from generador_datos_prueba.registro import Registro


@pytest.fixture
def registros_ejemplo() -> list[Registro]:
    """Provee registros de muestra representativos para pruebas de exportación."""
    return [
        {
            "campo": "telefono",
            "valor": "4170669074",
            "categoria": "validos",
            "valido": True,
            "motivo": "longitud 10 dentro del rango permitido [10, 10]",
        },
        {
            "campo": "email",
            "valor": "usuario+pruebas@ejemplo.com",
            "categoria": "validos",
            "valido": True,
            "motivo": "dirección válida con etiqueta (+)",
        },
        {
            "campo": "nombre",
            "valor": "Sofía Muñoz",
            "categoria": "validos",
            "valido": True,
            "motivo": "nombre con acentos y eñe",
        },
    ]


def test_csv_relectura_conserva_cinco_encabezados(tmp_path, registros_ejemplo):
    """Verifica que el CSV exportado conserve exactamente los cinco encabezados especificados."""
    ruta_csv = tmp_path / "salida.csv"
    exportar_csv(registros_ejemplo, salida=ruta_csv)

    with open(ruta_csv, mode="r", encoding="utf-8", newline="") as f:
        lector = csv.reader(f)
        encabezados = next(lector)
        filas = list(lector)

    assert encabezados == CAMPOS_REGISTRO, (
        f"Los encabezados obtenidos {encabezados} no coinciden con {CAMPOS_REGISTRO}"
    )
    assert len(filas) == len(registros_ejemplo)


def test_json_exportado_es_sintacticamente_valido(tmp_path, registros_ejemplo):
    """Verifica que el JSON exportado sea sintácticamente válido y deserializable."""
    ruta_json = tmp_path / "salida.json"
    exportar_json(registros_ejemplo, salida=ruta_json)

    with open(ruta_json, mode="r", encoding="utf-8") as f:
        datos_recuperados = json.load(f)

    assert isinstance(datos_recuperados, list)
    assert len(datos_recuperados) == len(registros_ejemplo)
    for original, recuperado in zip(registros_ejemplo, datos_recuperados):
        assert recuperado == original


@pytest.mark.parametrize("formato, funcion_exportar", [
    ("json", exportar_json),
    ("csv", exportar_csv),
])
def test_acentos_enie_y_emojis_sobreviven_en_utf8(tmp_path, formato, funcion_exportar):
    """Verifica que caracteres no ASCII (acentos, ñ, emojis complejos) se preserven intactos."""
    texto_unicode = "Sofía Muñoz Güemes 👨‍👩‍👧‍👦 👍🏽 ✨"
    motivo_unicode = "Validación con acentos (áéíóú), letra eñe (ñ/Ñ) y emojis compuestos"
    registros: list[Registro] = [
        {
            "campo": "texto",
            "valor": texto_unicode,
            "categoria": "hostiles",
            "valido": False,
            "motivo": motivo_unicode,
        }
    ]

    archivo = tmp_path / f"salida.{formato}"
    funcion_exportar(registros, salida=archivo)

    if formato == "json":
        with open(archivo, mode="r", encoding="utf-8") as f:
            datos = json.load(f)
            assert datos[0]["valor"] == texto_unicode
            assert datos[0]["motivo"] == motivo_unicode
    else:
        with open(archivo, mode="r", encoding="utf-8", newline="") as f:
            lector = csv.DictReader(f)
            filas = list(lector)
            assert filas[0]["valor"] == texto_unicode
            assert filas[0]["motivo"] == motivo_unicode


def test_valores_con_comas_comillas_y_saltos_no_rompen_csv(tmp_path):
    """Verifica que valores con delimitadores CSV (comas, comillas dobles y saltos) se escapen sin romper filas."""
    registros_complejos: list[Registro] = [
        {
            "campo": "texto",
            "valor": "primera parte, con coma, y más coma",
            "categoria": "hostiles",
            "valido": False,
            "motivo": "caso con comas internas",
        },
        {
            "campo": "texto",
            "valor": 'texto con "comillas dobles" y \'comillas simples\'',
            "categoria": "hostiles",
            "valido": False,
            "motivo": "caso con comillas",
        },
        {
            "campo": "texto",
            "valor": "primera línea\r\nsegunda línea con coma, y salto",
            "categoria": "hostiles",
            "valido": False,
            "motivo": "caso con salto de línea CRLF",
        },
        {
            "campo": "texto",
            "valor": "' OR 1=1; DROP TABLE usuarios, roles; --",
            "categoria": "hostiles",
            "valido": False,
            "motivo": "caso de inyección SQL con comas y comillas",
        },
    ]

    archivo_csv = tmp_path / "complejos.csv"
    exportar_csv(registros_complejos, salida=archivo_csv)

    with open(archivo_csv, mode="r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        filas = list(lector)

    assert len(filas) == len(registros_complejos), "La cantidad de filas releídas difiere por delimitadores rotos"

    for original, recuperada in zip(registros_complejos, filas):
        assert recuperada["campo"] == original["campo"]
        assert recuperada["valor"] == original["valor"]
        assert recuperada["categoria"] == original["categoria"]
        assert recuperada["motivo"] == original["motivo"]
        # En CSV los booleanos se serializan como texto 'True' o 'False'
        assert recuperada["valido"] == str(original["valido"])
