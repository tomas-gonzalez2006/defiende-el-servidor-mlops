# MLOps — Defiende el servidor

## Grupo

- Grupo: Visualización 2 de 2-4
- Suleily Estefania Moreno Contreras
- Tomás Alejandro González Forero

## Particiones reproducibles y experimentos

Los datos originales están en `data/raw/` y los artefactos de la partición en
`data/processed/`. La validación se deriva únicamente del CSV de entrenamiento.
Se agrupan todas las filas con los mismos predictores (excluyendo `id`, `label`
y `attack_cat`) antes de asignar el 20 % de grupos a validación; semilla fija:
42. Las filas con etiquetas contradictorias se conservan y permanecen juntas
en un mismo split. La asignación exacta por fila está en
`data/processed/split_assignment.csv`.

Instala las dependencias con `python -m pip install -r requirements.txt` y
ejecuta:

```powershell
python scripts\crear_splits.py
python scripts\entrenar_experimentos.py
```

Las referencias `data\raw.dvc` y `data\processed.dvc` y la caché DVC local ya
están creadas. No vuelvas a ejecutar `dvc init` en este workspace.

Los cuatro experimentos comparan dos regresiones logísticas, un árbol de
decisión y un bosque aleatorio. Todos usan el mismo split, la misma semilla,
preprocesamiento integrado en el pipeline y umbral 0.5. Se registran métricas
de validación, parámetros, hipótesis, huellas de datos, código y modelo completo
en MLflow. El test no se usa en esta etapa.

La auditoría del split está en `evidencias/splits.json`; la comparación se
exporta a `evidencias/experimentos.csv`. Para ver la interfaz local de MLflow,
abre otra terminal y ejecuta:

El almacén SQLite y los artefactos MLflow se guardan bajo
`%LOCALAPPDATA%\DefiendeElServidor\mlflow` porque Windows no admite este
backend SQLite/artefactos en la ruta UNC de WSL. Copias portables de los modelos
completos y métricas se guardan en `evidencias\mlflow\`.

```powershell
$localAppDataUri = $env:LOCALAPPDATA.Replace('\', '/')
$env:MLFLOW_TRACKING_URI = "sqlite:///$localAppDataUri/DefiendeElServidor/mlflow/mlflow.db"
mlflow ui --backend-store-uri $env:MLFLOW_TRACKING_URI --host 127.0.0.1 --port 5000
```

Luego abre <http://127.0.0.1:5000>. La interfaz es local a la máquina y no
está publicada en internet.

## Evaluación final

La versión congelada v2 se evaluó una sola vez sobre las 82.332 filas del test
completo. Los resultados están en `evidencias/metricas-test.json` y las
predicciones en `evidencias/predicciones-test.csv`. El script reproducible es
`scripts/evaluar_test.py`; `score_attack` es la probabilidad de la clase 1 y
se convierte a `y_pred` con umbral 0.5.

## DVC remote

Este workspace no tiene Git disponible y está montado desde WSL como ruta UNC.
Las referencias DVC se generaron con `--no-scm`; la caché local se incluye en
`.dvc/cache/`. El DVC para Windows no pudo adquirir su bloqueo en esta ruta UNC,
así que ejecuta operaciones DVC desde WSL nativo o mueve el proyecto a una ruta
local de Windows. Los datos no se han enviado a un remote.

Para que otra persona pueda recuperarlos, inicializa/controla el proyecto con
Git, configura un remote DVC compartido, autorizado y accesible por el
equipo/docente, y ejecuta `dvc push`. No se configura un destino de
almacenamiento sin confirmar su ubicación y permisos.
