# Changelog

Formato basado en principios de [Keep a Changelog](https://keepachangelog.com/), adaptado a un proyecto interno sin versionado semántico formal.

## [Sin publicar]

### Añadido
- Documentación del proyecto: `README.md`, `SECURITY.md` y la carpeta `docs/` (`FLUJO_DE_USO.md`, `SEGURIDAD_Y_PRIVACIDAD.md`, `SOLUCION_DE_PROBLEMAS.md`, `LIMPIEZA_DEL_HISTORIAL.md`).
- `.gitignore` para evitar el seguimiento de `perfil_uber/`, de los archivos generados en `salidas/` y de archivos comunes de entorno/IDE/sistema operativo.
- `.gitattributes` para normalizar finales de línea de archivos de texto.
- `salidas/.gitkeep` para conservar la carpeta de salida en el repositorio sin versionar su contenido.
- Pruebas automáticas de regresión (`tests/test_formatos_mxn.py`, con `unittest` de la biblioteca estándar) para los formatos monetarios de `MXN` reconocidos por `extraer_uber.py`.

### Corregido
- `extraer_uber.py` ahora reconoce importes en `MXN` tanto con el código de moneda como prefijo (`MXN 1,696.32`) como sufijo (`1,696.32 MXN`), incluyendo cantidades negativas en ambas variantes (`-MXN 1,184.55`, `MXN -1,184.55`, `-1,184.55 MXN`). Antes, solo el formato con `MXN` como sufijo se detectaba correctamente, lo que provocaba que en dispositivos donde Uber muestra `MXN` como prefijo se reportaran "0 filas detectadas" y no se generara el Excel.

### Cambiado
- Se dejó de rastrear en Git la carpeta `perfil_uber/` (perfil persistente de Chromium) y los archivos previamente generados en `salidas/`. Esto no modifica el comportamiento del programa; solo ajusta qué archivos locales quedan versionados. El contenido físico de estas carpetas se conserva en el equipo local.
- El patrón de detección de importes en `MXN` ahora se define una sola vez en Python (`PATRON_DINERO_TEXTO`) y se inserta en el JavaScript ejecutado en el DOM mediante sustitución de un marcador, en lugar de mantener dos expresiones regulares independientes que podían desincronizarse.

## Estado inicial

- Extracción manual asistida de la tabla de Ganancias de Uber mediante `login_uber.py` (inicio de sesión) y `extraer_uber.py` (captura y exportación a Excel), usando un perfil persistente de Chromium en `perfil_uber/`.
