---
library_name: scikit-learn
tags:
- unsw-nb15
- network-intrusion-detection
- mlops
---

# Defiende el servidor — v1

Pipeline completo de scikit-learn para clasificar conexiones normales (`label=0`)
y ataques (`label=1`) en UNSW-NB15. Incluye codificación categórica, escalado y
regresión logística (`C=1`, `solver=liblinear`, `max_iter=300`).

## Uso

```python
import joblib

pipeline = joblib.load("complete_pipeline.joblib")
score_attack = pipeline.predict_proba(rows)[:, 1]
y_pred = (score_attack >= 0.5).astype(int)
```

## Validación

- Recall de ataque: 0.9870
- Precision de ataque: 0.9244
- FPR: 0.1748
- Macro-F1: 0.9226
- Umbral: 0.5

## Trazabilidad

- Commit de código: `0b3cd416fecbc28e984ae2ebfa15f75050da497e`
- Run MLflow: `d5c932d1de7342a59fb754c384d9295d`
- Datos: UNSW-NB15, partición de entrenamiento y validación reproducible con semilla 42.

## Limitaciones

El modelo se entrenó con datos históricos de red y no garantiza el mismo
rendimiento en tráfico actual o en otros entornos. El test no se usó para
seleccionar esta versión.
