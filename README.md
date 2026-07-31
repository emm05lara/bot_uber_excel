# bot_uber_excel

Herramienta local en Python para extraer, mediante navegación manual asistida, las filas visibles de la tabla de **Ganancias** del panel de conductores/operadores de Uber y exportarlas a un archivo Excel.

> ⚠️ **Herramienta local y no oficial.** Este proyecto no está afiliado, respaldado ni verificado por Uber. Automatiza únicamente la lectura de lo que el usuario ya tiene visible en pantalla dentro de su propia sesión del navegador.

## Funcionalidades actuales

- Abre una ventana de Chromium (vía Playwright) con un **perfil de navegador persistente local** (`perfil_uber/`), de modo que la sesión iniciada se conserva entre ejecuciones.
- Permite iniciar sesión una sola vez con `login_uber.py` y reutilizar esa sesión después.
- Con `extraer_uber.py`, el usuario navega manualmente hasta la tabla de Ganancias, ajusta el rango de fechas y las filas visibles, y luego presiona **Enter** en la terminal para que el script lea el DOM y capture las filas visibles en ese momento.
- Detecta filas de la tabla buscando patrones de montos en `MXN` y separa los valores en columnas.
- Acumula filas sin duplicados entre distintas capturas (por ejemplo, al cambiar de página manualmente), usando el comando `fin` para terminar o `limpiar` para reiniciar el acumulado.
- Exporta el acumulado final a un archivo Excel dentro de `salidas/`.
- Guarda además un archivo de texto con los "candidatos" detectados en el DOM (para diagnóstico) y una captura de pantalla de la vista final.

**Lo que esta herramienta NO hace:**
- No inicia sesión de forma automática (el usuario debe autenticarse manualmente).
- No navega ni cambia de página, filtro o rango de fechas de forma automática: el usuario lo hace manualmente en el navegador antes de presionar Enter.
- No descarga automáticamente todas las páginas de resultados; cada captura corresponde a lo que esté visible en pantalla en ese momento.

## Flujo general de funcionamiento

1. El usuario ejecuta `login_uber.py` una vez para iniciar sesión manualmente en Uber. La sesión queda guardada en `perfil_uber/`.
2. El usuario ejecuta `extraer_uber.py`, que abre el navegador reutilizando esa sesión.
3. Dentro del navegador, el usuario navega manualmente a la sección de Ganancias, selecciona el rango de fechas y configura las filas visibles.
4. El usuario vuelve a la terminal y presiona Enter para que el script capture las filas visibles.
5. Si hay más páginas o vistas, el usuario cambia de página manualmente en el navegador y vuelve a presionar Enter para acumular más filas (sin duplicados).
6. El usuario escribe `fin` cuando termina, y el script exporta todo lo acumulado a un archivo Excel en `salidas/`.

## Requisitos

- Python 3 (recomendado 3.10 o superior).
- `pip`.
- Chromium administrado por Playwright (se instala aparte, no es el Chrome del sistema).

## Instalación recomendada (entorno virtual)

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Primer inicio de sesión

Ejecuta una sola vez (o cada vez que la sesión expire):

```bash
python login_uber.py
```

Se abrirá una ventana de Chromium. Inicia sesión manualmente en Uber y, cuando veas tu panel, vuelve a la terminal y presiona **Enter** para cerrar el navegador y guardar la sesión en `perfil_uber/`.

## Ejecución de la extracción

```bash
python extraer_uber.py
```

Procedimiento manual dentro del navegador que se abre:

1. Inicia sesión si Uber lo solicita nuevamente.
2. Entra manualmente a la sección **Ganancias**.
3. Selecciona manualmente el rango de fechas **personalizado** que quieras consultar.
4. Configura manualmente cuántas filas quieres visualizar en la tabla.
5. Vuelve a la terminal y presiona **Enter** para capturar la vista actual.
6. Si necesitas más datos, cambia manualmente de página o filtro en el navegador y presiona **Enter** de nuevo para acumular más filas (los duplicados se descartan automáticamente).
7. Escribe **`fin`** en la terminal para terminar y guardar el Excel con todo lo acumulado.
8. Escribe **`limpiar`** en cualquier momento para descartar lo acumulado hasta ahora y empezar de nuevo sin cerrar el navegador.

## Archivos generados

Cada ejecución de `extraer_uber.py` que produce resultados genera, dentro de `salidas/`:

- **Excel de ganancias** (`ganancias_uber_<fecha>.xlsx`): las filas acumuladas, exportadas con pandas.
- **Archivo de candidatos de diagnóstico** (`debug_candidatos_<fecha>.txt`): el detalle de los elementos del DOM que el script consideró como posibles filas, útil para depurar si algo no se detecta bien.
- **Captura de pantalla** (`captura_<fecha>.png`): una imagen de la página completa en el momento de la última captura.

Estos archivos **no se suben al repositorio** (ver `.gitignore`) porque pueden contener datos personales y financieros reales.

## Columnas exportadas

El Excel resultante contiene las siguientes columnas:

| Columna | Descripción |
|---|---|
| Nombre del conductor | Nombre detectado en la fila de la tabla |
| Ganancias totales | Monto en MXN |
| Reembolsos y gastos | Monto en MXN |
| Ajustes | Monto en MXN |
| Pago | Monto en MXN |
| Ganancias netas | Monto en MXN |

## Estructura del repositorio

```text
bot_uber_excel/
├── extraer_uber.py
├── login_uber.py
├── requirements.txt
├── README.md
├── SECURITY.md
├── CHANGELOG.md
├── .gitignore
├── .gitattributes
├── docs/
│   ├── FLUJO_DE_USO.md
│   ├── SEGURIDAD_Y_PRIVACIDAD.md
│   ├── SOLUCION_DE_PROBLEMAS.md
│   └── LIMPIEZA_DEL_HISTORIAL.md
└── salidas/
    └── .gitkeep
```

## Seguridad y privacidad

`perfil_uber/` guarda una sesión real del navegador y **no debe subirse al repositorio ni compartirse**. Los archivos generados en `salidas/` pueden contener nombres y datos financieros reales de conductores. Consulta [`docs/SEGURIDAD_Y_PRIVACIDAD.md`](docs/SEGURIDAD_Y_PRIVACIDAD.md) y [`SECURITY.md`](SECURITY.md) para más detalle.

## Solución de problemas

Consulta [`docs/SOLUCION_DE_PROBLEMAS.md`](docs/SOLUCION_DE_PROBLEMAS.md) para casos frecuentes (Chromium no instalado, errores de importación, sesión expirada, cero filas detectadas, etc.).

## Limitaciones actuales

- El proceso **requiere interacción manual** en varios pasos (inicio de sesión, navegación, selección de rango y de filas visibles, cambio de página). No es un proceso completamente automático.
- La detección de filas depende de que existan exactamente 5 montos en `MXN` visibles en el elemento; cambios en el formato de moneda o en la cantidad de columnas pueden afectar la detección.
- La herramienta **no descarga automáticamente todas las páginas**: el usuario debe cambiar de página o de filtro manualmente y volver a capturar.
- La interfaz de Uber puede cambiar en cualquier momento (nombres de botones, estructura del DOM, textos), lo cual puede afectar la detección de filas o de columnas.

## Aviso legal y de uso

La interfaz web de Uber puede cambiar sin previo aviso y afectar el funcionamiento de esta herramienta. El uso de este script debe cumplir con los **términos de servicio aplicables de Uber** y con las **políticas internas de la organización** que lo utilice. El usuario es responsable del uso que le dé a esta herramienta y a los datos que exporte con ella.
