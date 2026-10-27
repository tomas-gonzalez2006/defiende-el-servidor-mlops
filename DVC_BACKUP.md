# Respaldo DVC compartido

Esta guía explica cómo compartir y recuperar los datos DVC cuando todavía no se dispone de un remote DVC en línea.

## Archivo de respaldo

El respaldo está separado del ZIP de código:

```text
dvc-backup-20261027.zip
```

SHA-256 esperado:

```text
b822858c47c150dfb9a9dbd3f6ab7874756875324576b92a11ce20abad4f3960
```

Súbelo a una carpeta de Google Drive compartida con el docente y los integrantes. No lo incluyas dentro del repositorio GitHub ni dentro del ZIP de código.

## Comprobar y recuperar

```bash
sha256sum dvc-backup-20261027.zip
mkdir -p dvc-storage
unzip dvc-backup-20261027.zip -d dvc-storage
source .venv/bin/activate
dvc remote add -d backup-local /ruta/absoluta/dvc-storage
dvc pull
dvc status -c
```

El SHA debe coincidir con el anterior y el estado esperado es `Cache and remote 'backup-local' are in sync.` En Windows, usa una ruta equivalente como `C:/ruta/dvc-storage`.

## Limitación

Este respaldo permite recuperar los objetos DVC, pero no es un remote DVC servido por red. Para cumplir estrictamente el requisito del docente se debe reemplazar por S3, Google Cloud Storage, Azure, SSH o un almacenamiento institucional con permisos de lectura.

Nunca compartas archivos de credenciales, `.dvc/config.local` ni tokens.
