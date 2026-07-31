# Política de seguridad

Este proyecto es una herramienta local. No tiene backend, no expone servicios en red y no está pensado para almacenar credenciales.

## Qué nunca debe publicarse

- La carpeta `perfil_uber/` (perfil persistente de Chromium: puede contener cookies, tokens de sesión y datos locales de navegación).
- Los archivos generados en `salidas/` (Excel, capturas de pantalla y archivos de diagnóstico), ya que pueden contener nombres y datos financieros reales de conductores.
- Contraseñas, cookies, tokens, capturas de pantalla de sesiones iniciadas, o cualquier archivo dentro de `perfil_uber/` o `salidas/`.

## Cómo reportar una posible exposición

Si detectas que alguno de estos archivos fue publicado accidentalmente (por ejemplo, en un commit, un fork, un pull request o un issue):

1. **No** adjuntes el archivo sensible, ni su contenido, ni capturas de pantalla del mismo en el reporte.
2. Describe el problema en términos generales: qué tipo de archivo se expuso (perfil de navegador, Excel de salida, captura, etc.), en qué commit o ubicación, y desde cuándo.
3. Notifica directamente y en privado a quien administre el repositorio, en lugar de abrir un issue público, si el repositorio es público o tiene colaboradores externos.
4. Si la exposición incluye una sesión de Uber activa (contenida en `perfil_uber/`), cierra o revoca esa sesión desde la cuenta de Uber correspondiente lo antes posible.

Para el procedimiento técnico de retirar estos archivos del historial de Git, consulta [`docs/LIMPIEZA_DEL_HISTORIAL.md`](docs/LIMPIEZA_DEL_HISTORIAL.md).

## Alcance local de perfiles y salidas

`perfil_uber/` y `salidas/` son datos **locales** de cada usuario de la herramienta. No deben compartirse entre personas, equipos ni entornos, y no deben tratarse como respaldo ni como medio de transporte de datos.

## Uso de credenciales

Esta herramienta **no debe usarse para almacenar contraseñas, tokens ni credenciales** en el repositorio, en archivos de configuración versionados, ni en ningún archivo dentro de `docs/`. El inicio de sesión en Uber se realiza manualmente por el usuario en el navegador, y la sesión resultante se conserva únicamente de forma local en `perfil_uber/`.
