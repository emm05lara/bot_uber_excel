# Limpieza del historial de Git

## Punto de partida importante

Retirar una carpeta o archivo del **índice actual** de Git (por ejemplo, con `git rm -r --cached perfil_uber`) hace que Git deje de rastrear ese contenido **a partir de ese commit en adelante**. No elimina las versiones de ese contenido que ya quedaron guardadas en **commits anteriores** del historial.

Esto significa que, si `perfil_uber/` (o archivos de `salidas/`) estuvo alguna vez comprometido en un commit previo, ese contenido sigue siendo recuperable por cualquiera que tenga acceso al historial completo del repositorio, aunque ya no aparezca en el estado actual del proyecto.

> ⚠️ Este documento **no ejecuta ninguno de los comandos que describe**. Son alternativas explicativas para que el propietario del repositorio decida y actúe de forma deliberada, fuera del alcance de esta limpieza documental.

## Antes de hacer cualquier limpieza de historial

- **Haz un respaldo completo del repositorio** (incluyendo `.git/`) antes de intentar cualquiera de las siguientes alternativas.
- Ten presente que ambas alternativas son **operaciones destructivas sobre el historial**: cambian los identificadores de commit y pueden requerir **force-push**.
- Cualquier colaborador que tenga clonado el repositorio **deberá volver a clonarlo** después de una reescritura de historial; no podrá simplemente hacer `git pull`.
- Después de limpiar el historial, si el contenido expuesto incluía una sesión de Uber, **cierra o revoca esa sesión** desde la cuenta correspondiente (ver [`SEGURIDAD_Y_PRIVACIDAD.md`](SEGURIDAD_Y_PRIVACIDAD.md)). La limpieza del historial de Git no invalida por sí sola una sesión ya expuesta.

## Alternativa 1: reescribir el historial con `git filter-repo`

`git filter-repo` permite eliminar por completo un archivo o carpeta de todo el historial de commits, reescribiendo cada commit que lo contenía.

Ejemplo ilustrativo (no ejecutado):

```bash
# Instalar git-filter-repo si no está disponible
# (ver documentación oficial de la herramienta)

# Eliminar perfil_uber del historial completo
git filter-repo --path perfil_uber --invert-paths

# Eliminar también archivos previos de salidas/, si corresponde
git filter-repo --path salidas --invert-paths
```

Después de esto:

- El historial local queda reescrito con nuevos identificadores de commit.
- Se requiere `git push --force` (o `--force-with-lease`) para actualizar el remoto.
- Todos los colaboradores deben volver a clonar el repositorio; no deben intentar fusionar su copia anterior con la reescrita.

## Alternativa 2: crear un repositorio limpio desde cero

Cuando el proyecto todavía tiene poco historial (como es el caso actual), puede ser más simple y seguro crear un repositorio nuevo a partir del estado actual del código, sin arrastrar el historial antiguo.

Ejemplo ilustrativo (no ejecutado):

```bash
# Partiendo del estado actual ya limpio (sin perfil_uber ni salidas rastreados)
rm -rf .git
git init
git add .
git commit -m "Estado inicial limpio del proyecto"
```

Consideraciones:

- Esto descarta por completo el historial anterior (todos los commits previos), no solo el contenido sensible.
- Es una operación destructiva sobre el historial local; requiere respaldo previo del `.git` original si se quiere conservar por cualquier motivo.
- Si el repositorio ya existía en un remoto (por ejemplo, GitHub), publicar este nuevo historial también requerirá `force-push` sobre esa referencia remota, y los colaboradores deberán volver a clonar.

## Cuál alternativa elegir

Esta decisión corresponde al propietario del repositorio, considerando el historial real, la cantidad de colaboradores y si el repositorio ya fue clonado por terceros. Ninguna de las dos alternativas fue ejecutada como parte de esta limpieza documental.
