import argparse
import random
import sys
from collections.abc import Sequence

from generador_datos_prueba.exportar import exportar_csv, exportar_json
from generador_datos_prueba.generadores import email, nombre, telefono, texto


def _agregar_argumentos_comunes(
    parser: argparse.ArgumentParser,
    min_default: int | None = None,
    max_default: int | None = None,
) -> None:
    parser.add_argument(
        "--categoria",
        default="validos",
        help="Categoría de datos a generar (validos, invalidos, limite, hostiles).",
    )
    parser.add_argument(
        "--cantidad",
        type=int,
        default=None,
        help="Cantidad de registros a generar.",
    )
    parser.add_argument(
        "--formato",
        choices=["json", "csv"],
        default="json",
        help="Formato de exportación (json o csv; por defecto: json).",
    )
    parser.add_argument(
        "--salida",
        type=str,
        default=None,
        help="Ruta del archivo de salida (por defecto: stdout).",
    )
    parser.add_argument(
        "--semilla",
        type=int,
        default=None,
        help="Semilla entera para reproducibilidad del generador.",
    )
    parser.add_argument(
        "--min",
        dest="minimo",
        type=int,
        default=min_default,
        help=f"Valor mínimo aplicable al campo (por defecto: {min_default}).",
    )
    parser.add_argument(
        "--max",
        dest="maximo",
        type=int,
        default=max_default,
        help=f"Valor máximo aplicable al campo (por defecto: {max_default}).",
    )


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="datos-prueba",
        description="Generador de datos de prueba para QA.",
    )
    subparsers = parser.add_subparsers(
        dest="subcomando",
        title="subcomandos",
        description="Tipos de campos disponibles para generar",
        required=True,
    )

    # Subcomando: telefono
    parser_telefono = subparsers.add_parser(
        "telefono",
        help="Generar datos de prueba para números de teléfono.",
    )
    _agregar_argumentos_comunes(parser_telefono, min_default=10, max_default=10)

    # Subcomando: email
    parser_email = subparsers.add_parser(
        "email",
        help="Generar datos de prueba para direcciones de correo electrónico.",
    )
    _agregar_argumentos_comunes(parser_email)

    # Subcomando: nombre
    parser_nombre = subparsers.add_parser(
        "nombre",
        help="Generar datos de prueba para nombres de personas.",
    )
    _agregar_argumentos_comunes(parser_nombre, min_default=2, max_default=50)

    # Subcomando: texto
    parser_texto = subparsers.add_parser(
        "texto",
        help="Generar datos de prueba para cadenas de texto.",
    )
    _agregar_argumentos_comunes(parser_texto, min_default=1, max_default=255)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = crear_parser()
    args = parser.parse_args(argv)

    categorias_validas = {"validos", "invalidos", "limite", "hostiles"}
    if args.categoria not in categorias_validas:
        sys.stderr.write(
            f"error: categoría desconocida '{args.categoria}'. "
            f"Categorías permitidas: validos, invalidos, limite, hostiles.\n"
        )
        return 1

    if args.cantidad is not None and args.cantidad < 1:
        sys.stderr.write(f"error: --cantidad ({args.cantidad}) debe ser mayor o igual a 1\n")
        return 1

    if args.minimo is not None and args.minimo < 1:
        sys.stderr.write(f"error: --min ({args.minimo}) no puede ser menor que 1\n")
        return 1

    if args.minimo is not None and args.maximo is not None and args.minimo > args.maximo:
        sys.stderr.write(f"error: --min ({args.minimo}) no puede ser mayor que --max ({args.maximo})\n")
        return 1

    rng = random.Random(args.semilla)

    if args.subcomando == "telefono":
        minimo = 10 if args.minimo is None else args.minimo
        maximo = 10 if args.maximo is None else args.maximo
        registros = telefono.generar(
            categoria=args.categoria,
            cantidad=args.cantidad,
            rng=rng,
            minimo=minimo,
            maximo=maximo,
        )
    elif args.subcomando == "email":
        registros = email.generar(
            categoria=args.categoria,
            cantidad=args.cantidad,
            rng=rng,
            minimo=args.minimo,
            maximo=args.maximo,
        )
    elif args.subcomando == "nombre":
        minimo = 2 if args.minimo is None else args.minimo
        maximo = 50 if args.maximo is None else args.maximo
        registros = nombre.generar(
            categoria=args.categoria,
            cantidad=args.cantidad,
            rng=rng,
            minimo=minimo,
            maximo=maximo,
        )
    elif args.subcomando == "texto":
        minimo = 1 if args.minimo is None else args.minimo
        maximo = 255 if args.maximo is None else args.maximo
        registros = texto.generar(
            categoria=args.categoria,
            cantidad=args.cantidad,
            rng=rng,
            minimo=minimo,
            maximo=maximo,
        )
    else:
        registros = []

    try:
        if args.formato == "csv":
            exportar_csv(registros, salida=args.salida)
        else:
            exportar_json(registros, salida=args.salida)
    except OSError as e:
        sys.stderr.write(
            f"error: no se pudo escribir en el archivo de salida '{args.salida}': {e.strerror or e}\n"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
