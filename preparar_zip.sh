#!/usr/bin/env bash

# Preparar el ZIP final del proyecto
# Este script recopila los archivos y carpetas obligatorios y crea un archivo ZIP listo para entrega.

set -euo pipefail

ZIP_NAME="entrega_mlops_$(date +%Y%m%d_%H%M%S).zip"

# Carpetas y archivos obligatorios
declare -a paths=(
  "README.md"
  "entrega.md"
  "informe_mlop_defiende_servidor.pdf"
  "requirements.txt"
  "data/raw.dvc"
  "data/processed.dvc"
  "src/"
  "configs/"
  ".dvc/config"
  "src/"
  "configs/"
  ".dvcignore"
  "evidencias/"
  "scripts/"
  "versiones/"
  "publicacion/"
)

# Crear ZIP: no incluir datasets, cachés, entornos, credenciales ni configuración local.
rm -f "$ZIP_NAME"
zip -r "$ZIP_NAME" "${paths[@]}" -x 'evidencias/predicciones-test.csv' 'evidencias/mlflow/*/complete_pipeline.joblib'

echo "ZIP creado: $ZIP_NAME"

