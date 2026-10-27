# Entrega — MLOps: Defiende el servidor

## Integrantes

- Grupo: Visualización 2 de 2-4
- Suleily Estefania Moreno Contreras
- Tomás Alejandro González Forero

## Repositorios

- Código: https://github.com/tomas-gonzalez2006/defiende-el-servidor-mlops
- Modelos: https://huggingface.co/suliely/defiende-el-servidor-modelos
- Commit final de código: `6caa8e6` (documentación); commit completo anterior verificable: `cab7ef833cff5d5a22fb324ed49fbca10f6e3baa`.

## Versiones de modelo

### v1

- Modelo: regresión logística, `C=1`, umbral `0.5`.
- Commit de código: `0b3cd416fecbc28e984ae2ebfa15f75050da497e`.
- Run MLflow: `d5c932d1de7342a59fb754c384d9295d`.
- Revisión Hugging Face: `0341d2427932e8293296dc53532ace2eee14f59d`.
- Hash del artefacto: `b7b932bf4d40d7ab55e40c7326a08e578d2ec1231e4e308d83081fef1dd0e645`.

### v2

- Modelo: bosque aleatorio, 100 árboles, umbral `0.5`.
- Commit de código: `6428eb9abe8adfd9d9a19cd4df1eec7f4aa2737c`.
- Run MLflow: `423880e8c50744af8f47f60a5736a423`.
- Revisión Hugging Face: `b37867214a623bce29e946306e2d3e371cb45551`.
- Hash del artefacto: `ae10f2c351b3740b5c0ab8a43380f666b93eef4e4ce66b060e82e38a26f8665f`.

v2 fue seleccionada con validación porque mejora Macro-F1 y reduce FPR frente
a v1. La decisión está congelada en `evidencias/seleccion.json` antes del test.

## Datos y DVC

Los archivos están descritos por `data/raw.dvc` y `data/processed.dvc`.
El respaldo DVC operativo actual es local: `/home/suleily/dvc-storage`. La
configuración de Google Drive queda pendiente de un almacenamiento con cuota
para cuentas de servicio o de otro remote compartido autorizado. Esta
limitación está documentada en `evidencias/recuperacion/comandos.log`.

Como respaldo separado se generó `dvc-backup-20261027.tar.gz` fuera del ZIP de
código. Para usar un respaldo equivalente en otro equipo, extrae su contenido
en una carpeta y configúrala como remote local con `dvc remote add -d backup
/ruta/al/remote`; después ejecuta `dvc pull`. Este respaldo no sustituye un
remote compartido accesible por el docente.

## Resultados finales

La evaluación de v2 usó las 82.332 filas del test completo y está documentada
en `evidencias/metricas-test.json`. Las predicciones recalculables están en
`evidencias/predicciones-test.csv`.

## Instalación y reproducción

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
dvc pull
python scripts/crear_splits.py
python scripts/entrenar_experimentos.py
python scripts/evaluar_test.py
```

La prueba de recuperación usa 20 filas fijas y está en `evidencias/recuperacion/`.
El informe está disponible como `informe_mlop_defiende_servidor.pdf` y como
fuente LaTeX en `informe_mlop_defiende_servidor.tex`.

## Recursos y limitaciones

El procesamiento se realizó localmente con Python 3.14.4. Los artefactos de
modelos y datos ocupan aproximadamente 83 MB en la caché DVC y 12 MB para el
modelo v2. El test mostró un FPR mayor que validación, por lo que el rendimiento
puede cambiar en tráfico real o en otros periodos históricos.

## Uso de IA y contribuciones

Se utilizó un asistente de IA para apoyar la organización, escritura y revisión
de comandos y documentación. El grupo verificó localmente hashes, filas,
métricas, artefactos, recuperación y publicaciones. Suleily Estefania Moreno
Contreras y Tomás Alejandro González Forero realizaron conjuntamente la
preparación, evaluación y documentación del proyecto.

## Estado antes del envío

La revisión detallada está en `revision_estado.md`. Sigue pendiente un remote
DVC compartido con acceso para el docente y la confirmación de permisos de
lectura antes de enviar la entrega.
