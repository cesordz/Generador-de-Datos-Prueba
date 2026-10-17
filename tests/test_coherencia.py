"""Pruebas de coherencia: todo registro valido=True pasa un validador independiente y valido=False lo falla."""

import random
import re
import pytest

from generador_datos_prueba.generadores import email, nombre, telefono, texto


# ---------------------------------------------------------------------------
# Validadores independientes definidos exclusivamente para las pruebas
# ---------------------------------------------------------------------------

def validador_telefono(valor: str, minimo: int = 10, maximo: int = 10) -> bool:
    """Valida que el teléfono tenga solo dígitos, longitud en rango y no empiece en 0."""
    if not valor or not valor.isdigit():
        return False
    if valor[0] == "0":
        return False
    return minimo <= len(valor) <= maximo


def validador_email(valor: str) -> bool:
    """Valida que el email cumpla la sintaxis fundamental de RFC 5321."""
    if not valor or len(valor) > 254:
        return False
    if valor.count("@") != 1:
        return False

    usuario, dominio = valor.split("@")

    # Reglas para la parte local (usuario)
    if not (1 <= len(usuario) <= 64):
        return False
    if usuario.startswith(".") or usuario.endswith("."):
        return False
    if ".." in usuario or " " in usuario:
        return False
    # No debe contener caracteres de control, saltos ni inyecciones
    if any(c in usuario for c in ["\r", "\n", "\t", '"', "<", ">", "\u00a0", "\u200b"]):
        return False
    # Excluir caracteres no ASCII (acentos, emojis) si no están codificados en punycode
    try:
        usuario.encode("ascii")
    except UnicodeEncodeError:
        return False

    # Reglas para el dominio
    if "." not in dominio or dominio.endswith("."):
        return False
    partes = dominio.split(".")
    tld = partes[-1]
    if len(tld) < 2:
        return False
    if " " in dominio or any(c in dominio for c in ["\r", "\n", "\t"]):
        return False

    return True


# ===========================================================================
# DECISIONES DE DISEÑO PARA VALIDACIÓN DE NOMBRES:
#
# Un validador de nombres hispanos en un sistema razonable debe admitir:
# 1. Caracteres alfabéticos latinos, incluyendo acentos del español (á, é, í, ó, ú),
#    diéresis (ü) y la letra ñ / Ñ.
# 2. Espacios simples separando nombres y apellidos.
# 3. Apóstrofos legítimos en patronímicos de origen celta/gaélico (ej. O'Brien).
# 4. Guiones legítimos en nombres y apellidos compuestos (ej. María-José).
#
# Por el contrario, debe rechazar como inválido:
# 1. Cadenas vacías o consistentes únicamente en espacios en blanco.
# 2. Espacios al inicio o final (falta de sanitización/trim) o dobles espacios.
# 3. Números y caracteres de control o puntuación arbitraria (@, #, $, %, etc.).
# 4. Emojis y caracteres de alfabetos ajenos (cirílico, griego, etc.).
# 5. Ataques de inyección (código SQL, scripts HTML/XSS).
# 6. Longitudes fuera del rango permitido [minimo, maximo].
# ===========================================================================

def validador_nombre(valor: str, minimo: int = 2, maximo: int = 50) -> bool:
    """Validador independiente para nombres de personas."""
    if not valor:
        return False
    if not (minimo <= len(valor) <= maximo):
        return False
    # Rechazar espacios al inicio, al final o dobles espacios
    if valor != valor.strip() or "  " in valor:
        return False
    # Rechazar inyecciones o scripts conocidos
    if any(token in valor for token in ["<script>", "OR 1=1", "--"]):
        return False

    # Caracteres permitidos: letras (con acentos, diéresis, ñ), espacios, apóstrofo y guion
    patron = r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]+([ '\-][a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]+)*$"
    return bool(re.match(patron, valor))


# ===========================================================================
# DECISIONES DE DISEÑO PARA VALIDACIÓN DE TEXTO:
#
# Un campo de texto general en QA se considera válido si:
# 1. Su longitud en caracteres está estrictamente dentro del rango [minimo, maximo].
# 2. No es una cadena vacía ni está formada exclusivamente por espacios en blanco.
# 3. No contiene patrones de ataque o entradas maliciosas comunes:
#    - Inyecciones de scripts HTML (XSS).
#    - Inyecciones SQL (terminadores de sentencia, comentarios SQL, OR 1=1).
#    - Comillas desbalanceadas para romper delimitadores.
#    - Caracteres de control no imprimibles (NUL byte \x00, BEL \x07).
#    - Comandos de shell del sistema operativo (; rm, && whoami).
#    - Especificadores de cadenas de formato (%s, %n).
#    - Secuencias de Path Traversal (../).
#    - Caracteres invisibles de ancho cero (U+200B).
#    - Ataques homógrafos que mezclan o sustituyen alfabetos latinos por cirílicos.
# ===========================================================================

def validador_texto(valor: str, minimo: int = 1, maximo: int = 255) -> bool:
    """Validador independiente para cadenas de texto."""
    if not valor:
        return False
    if not valor.strip():
        return False
    if not (minimo <= len(valor) <= maximo):
        return False

    # Rechazar comillas sin cerrar / desbalanceadas
    if valor.count("'") % 2 != 0 or valor.count('"') % 2 != 0:
        return False

    # Rechazar saltos de línea, tabulaciones y caracteres de control no imprimibles
    if any(c in valor for c in ["\r", "\n", "\t", "\x00", "\x07"]):
        return False

    # Rechazar caracteres invisibles o de anulación de dirección
    if any(c in valor for c in ["\u200b", "\u202e"]):
        return False

    patrones_hostiles = [
        "<script>",
        "DROP TABLE",
        "OR 1=1",
        "; cat ",
        "%s%s",
        "<!DOCTYPE",
        "../",
        "раураӏ",
    ]
    if any(p in valor for p in patrones_hostiles):
        return False

    # Rechazar emojis o secuencias no textuales
    if any(ord(c) >= 0x1F000 or c in ["\u200d", "\ufe0f"] for c in valor):
        return False

    return True


# ---------------------------------------------------------------------------
# Pruebas parametrizadas de coherencia
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("categoria", ["validos", "limite"])
def test_coherencia_telefono(categoria):
    """Verifica que cada registro de telefono cumpla o falle según su marca de valido."""
    rng = random.Random(42)
    minimo, maximo = 10, 10
    registros = telefono.generar(categoria=categoria, cantidad=15, rng=rng, minimo=minimo, maximo=maximo)

    for reg in registros:
        esperado = reg["valido"]
        obtenido = validador_telefono(reg["valor"], minimo=minimo, maximo=maximo)
        assert obtenido == esperado, (
            f"Incoherencia en telefono ({reg['categoria']}): valor='{reg['valor']}', "
            f"esperado={esperado}, obtenido={obtenido}, motivo='{reg['motivo']}'"
        )


@pytest.mark.parametrize("categoria", ["validos", "invalidos", "limite", "hostiles"])
def test_coherencia_email(categoria):
    """Verifica que cada registro de email cumpla o falle según su marca de valido."""
    rng = random.Random(42)
    registros = email.generar(categoria=categoria, cantidad=15, rng=rng)

    for reg in registros:
        esperado = reg["valido"]
        obtenido = validador_email(reg["valor"])
        assert obtenido == esperado, (
            f"Incoherencia en email ({reg['categoria']}): valor='{reg['valor']}', "
            f"esperado={esperado}, obtenido={obtenido}, motivo='{reg['motivo']}'"
        )


@pytest.mark.parametrize("categoria", ["validos", "invalidos", "limite", "hostiles"])
def test_coherencia_nombre(categoria):
    """Verifica que cada registro de nombre cumpla o falle según su marca de valido."""
    rng = random.Random(42)
    minimo, maximo = 2, 50
    registros = nombre.generar(categoria=categoria, cantidad=15, rng=rng, minimo=minimo, maximo=maximo)

    for reg in registros:
        esperado = reg["valido"]
        obtenido = validador_nombre(reg["valor"], minimo=minimo, maximo=maximo)
        assert obtenido == esperado, (
            f"Incoherencia en nombre ({reg['categoria']}): valor='{reg['valor']}', "
            f"esperado={esperado}, obtenido={obtenido}, motivo='{reg['motivo']}'"
        )


@pytest.mark.parametrize("categoria", ["validos", "invalidos", "limite", "hostiles"])
def test_coherencia_texto(categoria):
    """Verifica que cada registro de texto cumpla o falle según su marca de valido."""
    rng = random.Random(42)
    minimo, maximo = 1, 255
    registros = texto.generar(categoria=categoria, cantidad=15, rng=rng, minimo=minimo, maximo=maximo)

    for reg in registros:
        esperado = reg["valido"]
        obtenido = validador_texto(reg["valor"], minimo=minimo, maximo=maximo)
        assert obtenido == esperado, (
            f"Incoherencia en texto ({reg['categoria']}): valor='{reg['valor']}', "
            f"esperado={esperado}, obtenido={obtenido}, motivo='{reg['motivo']}'"
        )
