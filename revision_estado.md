# Revisión de cumplimiento

## Completado y verificado

- GitHub, estructura, dependencias, Git, DVC local, MLflow y Hugging Face.
- Descarga, hashes, auditoría, partición sin fuga y evidencias de UNSW-NB15.
- Cuatro experimentos con run ID, métricas, matrices y modelos cargables.
- v1/v2 con commits distintos y selección previa al test.
- Publicación y descarga por SHA completo de v1 y v2 en Hugging Face.
- Evaluación única de v2 sobre las 82.332 filas del test.
- Recuperación en entorno temporal: predicciones de 20 filas reproducidas.
- README, entrega.md, informe PDF, fuente LaTeX y ZIP sin datos masivos.

## Pendientes reales

1. Sustituir `/home/suleily/dvc-storage` por un remote DVC compartido y repetir
   `dvc pull` en un entorno limpio desde ese almacenamiento. Google Drive en
   ``Mi unidad'' rechazó la cuenta de servicio por falta de cuota.
   Se dejó un respaldo separado `dvc-backup-20261027.tar.gz` de 22 MB, con
   SHA-256 `c0672d381f25619b089b18cc0ed1a05fc623070980a8ae7051ac8930edb2b3a2`.
2. Confirmar permisos de lectura del docente en GitHub, Hugging Face y el
   almacenamiento DVC compartido.
3. Enviar un único mensaje por Teams o correo institucional, con el ZIP, PDF,
   commit final, URLs, SHA de v1/v2 y ubicación del remote DVC.
4. Medir y registrar recursos del entrenamiento si el docente exige una medida
   específica; actualmente se documentan versión de Python y tamaños de
   artefactos, pero no un perfil completo de CPU/RAM del entrenamiento.

La evaluación de test no debe repetirse: el modelo y el umbral ya están
congelados.
