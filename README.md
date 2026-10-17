# Generador de Datos de Prueba

Herramienta de línea de comandos en Python diseñada para apoyar tareas de aseguramiento de calidad (QA). Permite generar conjuntos de datos clasificados en casos válidos, inválidos, límite y hostiles para campos habituales en aplicaciones: números de teléfono, correos electrónicos, nombres de personas y cadenas de texto. Los datos se pueden exportar tanto a formato JSON como a CSV.

---

## Características principales

- **Sin dependencias externas en producción:** Construida exclusivamente con la biblioteca estándar de Python (utiliza `argparse` para la interfaz de comandos).
- **Generadores puros y deterministas:** Todo el comportamiento aleatorio depende de una semilla configurable, lo que asegura que las pruebas sean totalmente reproducibles.
- **Categorización orientada a pruebas de software:**
  - `validos`: Entradas que cumplen con las reglas de negocio y sintaxis esperadas.
  - `invalidos`: Entradas erróneas habituales (errores de formato, tipos incompatibles o ausencias de datos).
  - `limite`: Valores calculados mediante análisis de valores frontera (BVA) a partir de umbrales mínimos y máximos.
  - `hostiles`: Entradas diseñadas para probar la resistencia del sistema frente a inyecciones de código, desbordamientos, caracteres especiales o problemas de codificación.
- **Exportación flexible:** Salida estándar o archivo en disco en formatos JSON o CSV con codificación UTF-8.

---

## Esquema de los registros

Cada dato generado contiene la siguiente estructura:

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `campo` | string | Subcomando o tipo de dato generado (`telefono`, `email`, `nombre`, `texto`). |
| `valor` | string | El contenido de prueba generado. |
| `categoria` | string | Categoría del caso (`validos`, `invalidos`, `limite`, `hostiles`). |
| `valido` | boolean | Indica si un sistema razonable debería aceptar (`true`) o rechazar (`false`) el valor. |
| `motivo` | string | Explicación técnica de la regla aplicada o del caso de prueba. |

---

## Instalación

Se requiere Python 3.11 o superior.

Clonar o descargar el repositorio e instalar en modo editable:

```bash
pip install -e .
```

Si deseas instalar también las dependencias para ejecutar las pruebas:

```bash
pip install -e ".[dev]"
```

Una vez instalado, la herramienta queda disponible en la terminal a través de los comandos `datos-prueba` o `casos-borde`.

---

## Uso y subcomandos

La estructura general de invocación es:

```bash
datos-prueba <subcomando> [opciones]
```

### Opciones comunes

- `--categoria {validos,invalidos,limite,hostiles}`: Define la categoría de prueba deseada (por defecto: `validos`).
- `--cantidad INT`: Cantidad de registros a generar (por defecto: 10 en casos aplicables). En la categoría `limite`, los casos frontera se calculan de manera exacta y esta opción se ignora.
- `--formato {json,csv}`: Formato de exportación (por defecto: `json`).
- `--salida RUTA`: Ruta del archivo donde se guardarán los resultados (por defecto: salida estándar).
- `--semilla INT`: Semilla numérica para reproducibilidad determinista.
- `--min INT`: Longitud o umbral mínimo aplicable al campo.
- `--max INT`: Longitud o umbral máximo aplicable al campo.

---

### Subcomandos disponibles

#### 1. Telefono
Genera números de teléfono basados en dígitos numéricos sin comenzar en 0. Valores por defecto: `--min 10 --max 10`.

```bash
# Casos límite para números entre 8 y 12 dígitos
datos-prueba telefono --categoria limite --min 8 --max 12 --semilla 42

# Generar 5 teléfonos válidos en formato CSV
datos-prueba telefono --categoria validos --cantidad 5 --formato csv
```

#### 2. Email
Genera direcciones de correo electrónico basadas en la especificación RFC 5321.
- `validos`: Variantes legítimas con subdominios, etiquetas (`+`), puntos simples y guiones.
- `invalidos`: Sin separador `@`, múltiples `@`, ausencia de dominio o usuario, puntos consecutivos y TLDs de un solo carácter.
- `limite`: Usuarios en el límite de 64 y 65 caracteres, así como correos totales en el límite de 254 y 255 caracteres.
- `hostiles`: Espacios invisibles (U+00A0, U+200B), mayúsculas en dominio, inyecciones XSS y saltos de línea CRLF.

```bash
datos-prueba email --categoria invalidos
datos-prueba email --categoria limite
```

#### 3. Nombre
Genera nombres de personas basados en datos hispanos con soporte completo de tildes y letra eñe. Valores por defecto: `--min 2 --max 50`.
- `validos`: Combinaciones de nombres y apellidos hispanos.
- `invalidos`: Cadenas vacías, solo números, símbolos y longitudes por debajo del mínimo.
- `hostiles`: Apóstrofos legítimos (`O'Brien`), guiones (`María-José`), caracteres en español (`Muñoz Güemes`), emojis, alfabetos ajenos e inyecciones SQL/XSS.

```bash
datos-prueba nombre --categoria validos --cantidad 3 --semilla 1
datos-prueba nombre --categoria hostiles
```

#### 4. Texto
Genera cadenas de texto genéricas. Valores por defecto: `--min 1 --max 255`.
- `validos`: Frases normales en lenguaje natural ajustadas al rango de longitud.
- `invalidos`: Cadenas vacías y cadenas de solo espacios.
- `limite`: Longitudes inmediatamente anterior, exacta y posterior a los límites configurados.
- `hostiles`: 15 vectores de ataque y casos patológicos (inyección SQL, XSS, saltos CRLF, caracteres nulos, secuencias de escape de directorio, texto de derecha a izquierda y cadenas de 10.000 caracteres).

```bash
datos-prueba texto --categoria limite --min 5 --max 20
datos-prueba texto --categoria hostiles --formato json --salida hostiles.json
```

---

## Ejecución de pruebas

El proyecto incluye pruebas automatizadas que validan reproducibilidad por semilla, coherencia contra validadores independientes, análisis de valores límite, integridad de exportación en UTF-8 y manejo de argumentos erróneos:

```bash
pytest
```
