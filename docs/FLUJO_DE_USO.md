# Flujo de uso

Este documento describe, paso a paso, cómo usar `bot_uber_excel` de principio a fin.

## 1. Instalación

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
source .venv/bin/activate
```

Luego, en cualquier sistema:

```bash
pip install -r requirements.txt
playwright install chromium
```

`playwright install chromium` descarga el navegador Chromium que Playwright administra por su cuenta; no reutiliza el Chrome instalado en el sistema.

## 2. Inicio de sesión inicial

```bash
python login_uber.py
```

Esto abre una ventana de Chromium apuntando a la URL configurada en `login_uber.py`. El usuario debe iniciar sesión manualmente (usuario, contraseña, verificación en dos pasos si aplica). Cuando el panel de Uber ya sea visible, se vuelve a la terminal y se presiona **Enter**. El script cierra el navegador y guarda la sesión.

## 3. Conservación local de la sesión

La sesión queda almacenada en la carpeta `perfil_uber/`, en la raíz del proyecto. Esta carpeta es un perfil persistente de Chromium administrado por Playwright (`launch_persistent_context`). Mientras exista y no expire la sesión de Uber, no debería ser necesario volver a ejecutar `login_uber.py` en cada uso.

`perfil_uber/` es local y no debe subirse a ningún repositorio ni compartirse (ver [`SEGURIDAD_Y_PRIVACIDAD.md`](SEGURIDAD_Y_PRIVACIDAD.md)).

## 4. Selección manual del periodo

Al ejecutar `extraer_uber.py`, se abre el navegador reutilizando la sesión guardada. Dentro de la ventana:

1. Si Uber pide iniciar sesión de nuevo, se hace manualmente.
2. Se navega manualmente a la sección **Ganancias**.
3. Se selecciona manualmente el rango de fechas **personalizado** deseado.
4. Se configura manualmente cuántas filas se quieren ver en la tabla.

Todo este paso es manual: el script no elige fechas ni filtros por sí mismo.

## 5. Captura de una vista

Cuando la tabla está lista en pantalla, se vuelve a la terminal donde corre `extraer_uber.py` y se presiona **Enter**. El script:

- Busca en el DOM los elementos visibles que contengan exactamente 5 montos en `MXN` (los que corresponden a una fila real de la tabla).
- Convierte esos montos a valores numéricos y extrae el nombre del conductor asociado.
- Muestra en la terminal cuántas filas detectó en esa vista.

## 6. Acumulación entre páginas

Cada fila detectada se agrega a un acumulado interno, usando como clave la combinación de nombre y los cinco montos, para evitar filas duplicadas si se vuelve a capturar la misma vista.

Si hay más datos que revisar (más páginas, otro rango, otro filtro), se cambia manualmente en el navegador y se presiona **Enter** de nuevo en la terminal para capturar y acumular la nueva vista.

## 7. Comandos `fin` y `limpiar`

Después de cada captura, la terminal ofrece tres opciones:

- **Enter** (vacío): ya se ajustó la vista manualmente, capturar de nuevo.
- **`fin`**: terminar la sesión de captura y exportar todo lo acumulado a Excel.
- **`limpiar`**: descartar todo lo acumulado hasta ese momento y empezar de nuevo, sin cerrar el navegador.

## 8. Ubicación de los resultados

Al terminar con `fin` (y si se detectó al menos una fila en algún momento), se generan en la carpeta `salidas/`:

- `ganancias_uber_<fecha_hora>.xlsx`
- `debug_candidatos_<fecha_hora>.txt`
- `captura_<fecha_hora>.png`

La terminal muestra la ruta exacta de cada archivo generado al finalizar.
