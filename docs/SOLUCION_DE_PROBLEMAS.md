# Solución de problemas

Este documento cubre situaciones frecuentes. Salvo que se indique explícitamente lo contrario, ninguna de las indicaciones aquí implica cambios en el código de `extraer_uber.py` o `login_uber.py`.

Cuando una causa u solución no ha sido verificada directamente en este proyecto, se marca explícitamente como **hipótesis**.

## Chromium no instalado

Si Playwright no encuentra el navegador, ejecuta:

```bash
playwright install chromium
```

Esto descarga el Chromium administrado por Playwright, independiente del navegador que ya tengas instalado en el sistema.

## Error al importar Playwright

Si al ejecutar `login_uber.py` o `extraer_uber.py` aparece un error de tipo `ModuleNotFoundError: No module named 'playwright'`:

- Confirma que el entorno virtual esté activado.
- Confirma que `pip install -r requirements.txt` se ejecutó sin errores dentro de ese entorno.

**Hipótesis:** si el error persiste, puede deberse a tener más de un entorno de Python instalado y estar ejecutando el script fuera del entorno virtual donde se instaló Playwright.

## Error al importar pandas

Si aparece `ModuleNotFoundError: No module named 'pandas'`, aplica la misma verificación que con Playwright: entorno virtual activo y `requirements.txt` instalado correctamente en ese entorno.

## Uber solicita iniciar sesión nuevamente

Los scripts reutilizan la sesión guardada en `perfil_uber/`, pero esa sesión puede expirar por políticas propias de Uber (tiempo de inactividad, cierre de sesión remoto, cambios de seguridad en la cuenta, etc.).

Si Uber pide iniciar sesión de nuevo dentro de `extraer_uber.py`, hazlo manualmente en esa misma ventana; el script está preparado para continuar después de que la tabla de Ganancias sea visible. Si el problema es persistente, vuelve a ejecutar `login_uber.py` para renovar la sesión guardada.

## No se encuentran valores `MXN`

`extraer_uber.py` espera encontrar texto con el patrón de monto en `MXN` visible en pantalla antes de intentar capturar filas. Si aparece el mensaje "No encontré valores con MXN en pantalla":

- Verifica que la tabla de Ganancias esté realmente visible antes de presionar Enter en la terminal.
- Verifica que el rango de fechas seleccionado tenga datos (por ejemplo, un rango sin movimientos puede no mostrar montos).

**Hipótesis:** si la cuenta de Uber está configurada en otra moneda distinta de pesos mexicanos (MXN), es posible que la tabla no muestre montos en ese formato y el script no los detecte, ya que el patrón de búsqueda está fijado a `MXN`.

## Se detectan cero filas

Si el script se ejecuta pero reporta "0 filas detectadas en esta vista":

- Revisa el archivo `debug_candidatos_<fecha>.txt` generado en `salidas/`; ahí se listan los elementos que el script sí consideró como candidatos, aunque no hayan pasado el filtro final de una fila válida.
- Revisa la captura de pantalla (`captura_<fecha>.png`) generada en el mismo momento, para comparar visualmente qué estaba en pantalla.
- Confirma que la tabla tenga filas con exactamente 5 montos visibles (Ganancias totales, Reembolsos y gastos, Ajustes, Pago, Ganancias netas); es el criterio que usa el script para reconocer una fila real.

## Se genera la captura, pero se detectan cero filas

Síntoma:

- Uber está visible y la tabla de Ganancias tiene datos;
- la captura de pantalla se genera correctamente;
- la terminal muestra "Filas detectadas en esta vista: 0" de forma consistente, incluso con la tabla bien cargada.

Causa histórica:

- algunas variantes de la interfaz de Uber muestran el código de moneda antes del importe (por ejemplo `MXN 1,696.32` o `MXN -1,184.55`), en lugar de después (`1,696.32 MXN`);
- versiones anteriores de `extraer_uber.py` solo reconocían correctamente el formato con `MXN` después del importe, por lo que ninguna fila alcanzaba las 5 cantidades requeridas y el análisis monetario las descartaba todas.

Verificación:

- confirma que estás usando una versión de `extraer_uber.py` que incluye la corrección para formatos monetarios con `MXN` como prefijo o sufijo (incluyendo cantidades negativas);
- ejecuta las pruebas automáticas de regresión: `python -m unittest discover -s tests -v`;
- no publiques ni compartas el archivo de debug generado (`debug_candidatos_<fecha>.txt`) para diagnosticar este caso, porque puede contener nombres de conductores y montos reales (ver [`SEGURIDAD_Y_PRIVACIDAD.md`](SEGURIDAD_Y_PRIVACIDAD.md)).

## La interfaz de Uber cambió

Uber puede modificar en cualquier momento el diseño, los textos o la estructura del DOM de su panel. Como el script depende de patrones de texto y de la cantidad de montos `MXN` visibles por elemento, un cambio de interfaz puede hacer que:

- Se detecten menos filas de las esperadas, o ninguna.
- Se detecten elementos que no son filas reales.

En ese caso, el archivo de debug y la captura de pantalla son el punto de partida para entender qué cambió. Este documento no propone una corrección de código, conforme al alcance de esta limpieza documental.

## Problemas de permisos al escribir en `salidas/`

Si el script falla al crear archivos dentro de `salidas/`:

- Verifica que la carpeta `salidas/` exista y que el usuario del sistema operativo tenga permisos de escritura sobre ella.
- **Hipótesis:** en Windows, esto puede ocurrir si la carpeta está sincronizada con un servicio en la nube (como OneDrive) y el archivo está bloqueado temporalmente por ese servicio.

## El archivo Excel está abierto en otro programa

Si `ganancias_uber_<fecha>.xlsx` no se puede escribir porque ya está abierto en Excel u otro programa en el momento en que el script intenta generarlo, ciérralo antes de volver a ejecutar la extracción. Cada ejecución genera un archivo con marca de fecha y hora distinta, por lo que no debería sobrescribir un archivo previamente cerrado.

## Cómo conservar evidencias de diagnóstico sin publicarlas

Si necesitas conservar el archivo de debug o la captura de pantalla para investigar un problema:

- Guárdalos localmente en un equipo autorizado, no en un repositorio ni en un servicio de mensajería abierto.
- No los adjuntes en issues públicos ni los compartas fuera del equipo autorizado (ver [`SEGURIDAD_Y_PRIVACIDAD.md`](SEGURIDAD_Y_PRIVACIDAD.md)).
- Si necesitas compartir el problema con alguien más, describe el comportamiento observado y, si hace falta evidencia visual, recorta o difumina manualmente los datos personales y financieros antes de compartir la imagen.
