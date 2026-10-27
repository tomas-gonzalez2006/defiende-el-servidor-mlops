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

El proyecto fue verificado con Python 3.14.4. Instala las dependencias con:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Para regenerar la partición y ejecutar los cuatro experimentos:

```bash
python scripts/crear_splits.py
python scripts/entrenar_experimentos.py
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

Las referencias DVC se generaron con `--no-scm`. El remote compartido de Google
Drive está configurado en `.dvc/config`, pero la cuenta personal no puede usar
la cuota de una cuenta de servicio en `Mi unidad`. El remote operativo actual es
`local-storage`, en `/home/suleily/dvc-storage`, solo como respaldo temporal de
este equipo.

Para recuperar los datos desde el remote actualmente disponible:

```bash
source .venv/bin/activate
dvc pull
```

Antes de la entrega, sustituye el remote local por un almacenamiento compartido
autorizado para que otra persona pueda recuperar los datos sin depender de este
equipo. No se deben publicar tokens ni archivos JSON de credenciales.

## Modelos y predicción

Las versiones publicadas están en Hugging Face:

- [v1 — regresión logística](https://huggingface.co/suliely/defiende-el-servidor-modelos/tree/v1)
- [v2 — bosque aleatorio](https://huggingface.co/suliely/defiende-el-servidor-modelos/tree/v2)

Cada revisión contiene el pipeline completo, incluido el preprocesamiento. Para
descargar v2 por su SHA completo:

```bash
hf download suliely/defiende-el-servidor-modelos \
  --revision b37867214a623bce29e946306e2d3e371cb45551 \
  --repo-type model --local-dir modelos/v2
```

El pipeline se carga con `joblib.load` y produce `score_attack` con
`predict_proba`; la clase ataque es 1 y se aplica el umbral 0.5.

## Evidencias y recuperación

- Auditoría consolidada: `evidencias/auditoria.json`.
- Comparación de experimentos: `evidencias/experimentos.csv`.
- Selección v1/v2: `evidencias/seleccion.json`.
- Evaluación final: `evidencias/metricas-test.json` y `evidencias/predicciones-test.csv`.
- Prueba de recuperación: `evidencias/recuperacion/`.
- Código de evaluación: `scripts/evaluar_test.py`.
- Guía del respaldo DVC: `DVC_BACKUP.md`.
