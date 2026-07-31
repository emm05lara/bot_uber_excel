# Seguridad y privacidad

## Por qué `perfil_uber/` nunca debe subirse

`perfil_uber/` es un perfil persistente de Chromium creado por Playwright (`launch_persistent_context`). Es el mecanismo que permite conservar la sesión de Uber entre ejecuciones sin volver a iniciar sesión cada vez.

Por su naturaleza, un perfil de navegador puede contener:

- Cookies y tokens de sesión activos.
- Historial y datos de navegación local (caché, almacenamiento local, bases de datos internas del navegador).
- Cualquier otra información que el navegador guarde para mantener la sesión iniciada.

Si esta carpeta se publica (por ejemplo, en un repositorio público, un ZIP compartido o un backup accesible por terceros), cualquiera con acceso a ella podría potencialmente reutilizar la sesión guardada como si fuera el usuario legítimo, sin necesidad de conocer la contraseña.

## Qué puede contener `salidas/`

Los archivos generados por `extraer_uber.py` en `salidas/` (Excel, archivo de debug y captura de pantalla) reflejan exactamente lo que estaba visible en la tabla de Ganancias en el momento de la captura. Esto incluye, típicamente:

- Nombres de conductores.
- Montos financieros (ganancias totales, reembolsos, ajustes, pagos, ganancias netas).

Es decir, son datos personales y financieros reales, no datos de prueba.

## Dónde deben almacenarse los resultados

Los archivos de `salidas/`, así como `perfil_uber/`, deben almacenarse **únicamente en equipos autorizados** por la organización, con los controles de acceso que esa organización ya tenga definidos para datos financieros y personales de conductores.

## Qué no se debe compartir públicamente

- `perfil_uber/` completa o parcial.
- Cualquier archivo de `salidas/` (Excel, `.txt` de debug, capturas de pantalla).
- Fragmentos de esos archivos pegados en chats, tickets, issues o documentación no controlada.

## Qué no incluir en issues o reportes

Al reportar un problema sobre esta herramienta (por ejemplo, en un issue de este repositorio), **no incluyas**:

- Contraseñas.
- Cookies o tokens de sesión.
- Capturas de pantalla que muestren nombres de conductores o montos reales.
- Archivos de `salidas/` o de `perfil_uber/` adjuntos.

Si necesitas ilustrar un problema, describe el comportamiento (por ejemplo, "se detectaron 0 filas con el rango X") sin adjuntar los datos reales, o usa datos ficticios equivalentes.

## Qué hacer si se publica accidentalmente un perfil o una salida

1. Deja de usar esa sesión de inmediato: cierra o revoca la sesión de Uber correspondiente desde la cuenta afectada (por ejemplo, cerrando sesión en todos los dispositivos desde la configuración de la cuenta, si esa opción existe).
2. Retira el archivo o carpeta del seguimiento de Git si aún sigue rastreado (ver procedimiento en [`LIMPIEZA_DEL_HISTORIAL.md`](LIMPIEZA_DEL_HISTORIAL.md)).
3. Ten en cuenta que quitar un archivo del commit actual **no lo elimina de commits anteriores**; si el repositorio fue público o tuvo colaboradores externos en algún momento, considera esos datos como potencialmente expuestos y actúa en consecuencia (revocar sesión, notificar a quien corresponda según la política interna).
4. Evalúa con quien administre el proyecto si es necesario reescribir el historial de Git (ver [`LIMPIEZA_DEL_HISTORIAL.md`](LIMPIEZA_DEL_HISTORIAL.md)) para retirar el contenido también de commits anteriores.
