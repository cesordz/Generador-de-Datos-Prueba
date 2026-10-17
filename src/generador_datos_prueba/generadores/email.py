"""Generador de datos de prueba para direcciones de correo electrónico."""

import random
import sys


# Para este generador, una dirección de correo electrónico se considera "válida" si
# cumple con la especificación básica de RFC 5321: consta de una parte local (máximo
# 64 caracteres) compuesta por caracteres alfanuméricos y símbolos permitidos (. + _ -),
# seguida de '@' y un nombre de dominio con al menos un punto y un TLD de 2 o más caracteres,
# con una longitud total que no supera los 254 caracteres.


def _generar_valido(rng: random.Random) -> tuple[str, str]:
    """Genera una dirección de correo válida y su motivo específico usando rng."""
    usuarios = ["usuario", "juan", "maria", "contacto", "soporte", "admin", "dev"]
    etiquetas = ["notificaciones", "pruebas", "qa", "newsletter", "alertas"]
    dominios = ["ejemplo", "empresa", "correo", "servicio", "plataforma"]
    subdominios = ["app", "mail", "corp", "lab", "api"]
    tlds = ["com", "org", "net", "io", "es"]

    variante = rng.randint(0, 4)

    if variante == 0:
        # Puntos simples en la parte local
        usr1 = rng.choice(usuarios)
        usr2 = rng.choice(usuarios)
        dom = rng.choice(dominios)
        tld = rng.choice(tlds)
        return f"{usr1}.{usr2}@{dom}.{tld}", "dirección válida con punto simple en la parte local"

    elif variante == 1:
        # Signo '+' para alias/etiquetas
        usr = rng.choice(usuarios)
        tag = rng.choice(etiquetas)
        dom = rng.choice(dominios)
        tld = rng.choice(tlds)
        return f"{usr}+{tag}@{dom}.{tld}", "dirección válida con etiqueta (+)"

    elif variante == 2:
        # Subdominios
        usr = rng.choice(usuarios)
        sub = rng.choice(subdominios)
        dom = rng.choice(dominios)
        tld = rng.choice(tlds)
        return f"{usr}@{sub}.{dom}.{tld}", "dirección válida con subdominio"

    elif variante == 3:
        # Guiones y números
        usr = rng.choice(usuarios)
        num = rng.randint(1, 999)
        dom = rng.choice(dominios)
        tld = rng.choice(tlds)
        return f"{usr}-{num}@{dom}-qa.{tld}", "dirección válida con guiones y números"

    else:
        # Combinación de punto, etiqueta y subdominio
        usr1 = rng.choice(usuarios)
        usr2 = rng.choice(usuarios)
        num = rng.randint(1, 99)
        sub = rng.choice(subdominios)
        dom = rng.choice(dominios)
        tld = rng.choice(tlds)
        return (
            f"{usr1}.{usr2}+test{num}@{sub}.{dom}.{tld}",
            "dirección válida combinando puntos, etiqueta (+) y subdominio",
        )


def _obtener_casos_invalidos() -> list[tuple[str, str]]:
    """Devuelve la lista canónica de casos de prueba inválidos."""
    return [
        ("usuarioejemplo.com", "falta el separador @"),
        ("usuario@@ejemplo.com", "múltiples separadores @ no permitidos"),
        ("usuario@", "falta la parte del dominio"),
        ("@ejemplo.com", "falta la parte local (usuario)"),
        ("usuario..nombre@ejemplo.com", "puntos consecutivos en la parte local"),
        (".usuario@ejemplo.com", "punto al inicio de la parte local"),
        ("usuario.@ejemplo.com", "punto al final de la parte local"),
        ("usuario nombre@ejemplo.com", "espacio en medio de la dirección"),
        ("usuario@localhost", "dominio sin punto ni TLD"),
        ("usuario@ejemplo.c", "TLD de un solo carácter no permitido"),
    ]


def _obtener_casos_limite() -> list[tuple[str, bool, str]]:
    """Devuelve los casos límite de RFC 5321 (64/65 parte local, 254/255 total)."""
    # 1. Usuario de 64 caracteres (límite máximo permitido de parte local)
    usr_64 = "a" * 64
    email_usr_64 = f"{usr_64}@ejemplo.com"

    # 2. Usuario de 65 caracteres (excede el límite de parte local)
    usr_65 = "a" * 65
    email_usr_65 = f"{usr_65}@ejemplo.com"

    # 3. Dirección total de 254 caracteres (límite máximo total permitido)
    # "usuario@" mide 8 caracteres. Restan 246 caracteres para el dominio.
    # 60 + 1 + 60 + 1 + 60 + 1 + 59 + 1 + 3 = 246 caracteres de dominio
    dom_246 = f"{'a' * 60}.{'b' * 60}.{'c' * 60}.{'d' * 59}.com"
    email_total_254 = f"usuario@{dom_246}"

    # 4. Dirección total de 255 caracteres (excede el límite total permitido)
    # 60 + 1 + 60 + 1 + 60 + 1 + 60 + 1 + 3 = 247 caracteres de dominio
    dom_247 = f"{'a' * 60}.{'b' * 60}.{'c' * 60}.{'d' * 60}.com"
    email_total_255 = f"usuario@{dom_247}"

    return [
        (email_usr_64, True, "parte local en el límite máximo de 64 caracteres"),
        (email_usr_65, False, "parte local excede el límite de 64 caracteres (65 caracteres)"),
        (email_total_254, True, "dirección en el límite máximo total de 254 caracteres"),
        (email_total_255, False, "dirección excede el límite máximo total de 254 caracteres (255 caracteres)"),
    ]


def _obtener_casos_hostiles() -> list[tuple[str, bool, str]]:
    """Devuelve los casos de prueba con entradas hostiles."""
    return [
        ("  usuario@ejemplo.com  ", False, "espacios al inicio y al final"),
        ("usuario\u00a0nombre@ejemplo.com", False, "espacio no separable (U+00A0)"),
        ("usu\u200bario@ejemplo.com", False, "carácter de ancho cero (U+200B)"),
        ("usuario@EJEMPLO.COM", True, "dominio en mayúsculas"),
        ("usuário@ejemplo.com", False, "caracteres con acentos en la parte local"),
        ("usuario✨@ejemplo.com", False, "carácter emoji en la parte local"),
        ("usuario\r\n@ejemplo.com", False, "saltos de línea inyectados"),
        ("<script>alert(1)</script>@ejemplo.com", False, "etiqueta <script> en la parte local"),
        ('usuario"malicioso@ejemplo.com', False, "comillas dobles no balanceadas ni escapadas"),
    ]


def generar(
    categoria: str,
    cantidad: int | None,
    rng: random.Random,
    minimo: int | None = None,
    maximo: int | None = None,
) -> list[dict]:
    """Genera registros de datos de prueba para el campo email."""
    if minimo is not None or maximo is not None:
        sys.stderr.write("aviso: --min y --max no aplican para 'email' y se ignoran.\n")

    registros: list[dict] = []

    if categoria == "validos":
        total = 10 if cantidad is None else cantidad
        for _ in range(total):
            valor, motivo = _generar_valido(rng)
            registros.append(
                {
                    "campo": "email",
                    "valor": valor,
                    "categoria": "validos",
                    "valido": True,
                    "motivo": motivo,
                }
            )

    elif categoria == "invalidos":
        casos = _obtener_casos_invalidos()
        total = len(casos) if cantidad is None else cantidad
        for i in range(total):
            valor, motivo = casos[i % len(casos)]
            registros.append(
                {
                    "campo": "email",
                    "valor": valor,
                    "categoria": "invalidos",
                    "valido": False,
                    "motivo": motivo,
                }
            )

    elif categoria == "limite":
        if cantidad is not None:
            sys.stderr.write("aviso: --cantidad no aplica para la categoría 'limite' y se ignora.\n")

        for valor, valido, motivo in _obtener_casos_limite():
            registros.append(
                {
                    "campo": "email",
                    "valor": valor,
                    "categoria": "limite",
                    "valido": valido,
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
                    "campo": "email",
                    "valor": valor,
                    "categoria": "hostiles",
                    "valido": valido,
                    "motivo": motivo,
                }
            )

    return registros
