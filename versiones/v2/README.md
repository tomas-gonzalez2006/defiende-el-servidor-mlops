# v2 — Bosque aleatorio

Versión seleccionada únicamente con validación frente a v1.

- Familia: bosque aleatorio
- Configuración: `n_estimators=100`, `max_depth=20`, `min_samples_leaf=10`, `n_jobs=-1`
- Umbral: `0.5`
- Run MLflow: `423880e8c50744af8f47f60a5736a423`
- Artefacto completo: `evidencias/mlflow/423880e8c50744af8f47f60a5736a423/complete_pipeline.joblib`
- Macro-F1 de validación: `0.9415303815941589`
- Recall de ataque: `0.9826776886968803`
- Precision de ataque: `0.9470734246136601`
- FPR: `0.11885282747460217`

El cambio real frente a v1 es la familia del modelo y sus hiperparámetros: el
bosque reduce el FPR y mejora Macro-F1, aceptando una pequeña reducción del
recall de ataques.
