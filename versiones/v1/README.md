# v1 — Regresión logística

Modelo de referencia seleccionado únicamente con validación.

- Familia: regresión logística
- Configuración: `C=1`, `solver=liblinear`, `max_iter=300`
- Umbral: `0.5`
- Run MLflow: `d5c932d1de7342a59fb754c384d9295d`
- Artefacto completo: `evidencias/mlflow/d5c932d1de7342a59fb754c384d9295d/complete_pipeline.joblib`
- Macro-F1 de validación: `0.9225871938932528`
- Recall de ataque: `0.9869978814439413`
- Precision de ataque: `0.9243697478991597`
- FPR: `0.17477299289759957`

El pipeline contiene el preprocesamiento y el estimador.
