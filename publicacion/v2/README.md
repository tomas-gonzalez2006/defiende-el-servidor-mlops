---
library_name: scikit-learn
tags:
- unsw-nb15
- network-intrusion-detection
- mlops
---

# Defiende el servidor — v2

Pipeline completo de scikit-learn para clasificar conexiones normales (`label=0`)
y ataques (`label=1`) en UNSW-NB15. Incluye codificación categórica, escalado y
bosque aleatorio de 100 árboles (`max_depth=20`, `min_samples_leaf=10`).

## Uso

```python
import joblib

pipeline = joblib.load("complete_pipeline.joblib")
score_attack = pipeline.predict_proba(rows)[:, 1]
y_pred = (score_attack >= 0.5).astype(int)
```

## Validación

- Recall de ataque: 0.9827
- Precision de ataque: 0.9471
- FPR: 0.1189
- Macro-F1: 0.9415
- Umbral: 0.5

## Trazabilidad

- Commit de código: `6428eb9abe8adfd9d9a19cd4df1eec7f4aa2737c`
- Run MLflow: `423880e8c50744af8f47f60a5736a423`
- Datos: UNSW-NB15, partición de entrenamiento y validación reproducible con semilla 42.

## Limitaciones

El modelo se entrenó con datos históricos de red y no garantiza el mismo
rendimiento en tráfico actual o en otros entornos. El test no se usó para
seleccionar esta versión.
