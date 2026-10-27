"""Evaluate the frozen v2 pipeline once on the complete published test split."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score


ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = ROOT / "data" / "raw" / "UNSW_NB15_testing-set.csv"
MODEL_PATH = ROOT / "publicacion" / "v2" / "complete_pipeline.joblib"
SELECTION_PATH = ROOT / "evidencias" / "seleccion.json"
OUTPUT_DIR = ROOT / "evidencias"
PREDICTIONS_PATH = OUTPUT_DIR / "predicciones-test.csv"
METRICS_PATH = OUTPUT_DIR / "metricas-test.json"
TARGET = "label"
THRESHOLD = 0.5


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    test = pd.read_csv(TEST_PATH, low_memory=False)
    pipeline = joblib.load(MODEL_PATH)
    selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))

    features = [
        column for column in test.columns if column not in {"id", "attack_cat", TARGET}
    ]
    scores = pipeline.predict_proba(test[features])[:, 1]
    predictions = (scores >= THRESHOLD).astype(int)
    y_true = test[TARGET].astype(int).to_numpy()
    matrix = confusion_matrix(y_true, predictions, labels=[0, 1])
    tn, fp, fn, tp = matrix.ravel()

    output = pd.DataFrame(
        {
            "row_id": [f"UNSW_NB15_testing-set.csv:{index}" for index in range(len(test))],
            "y_true": y_true,
            "score_attack": scores,
            "y_pred": predictions,
        }
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(PREDICTIONS_PATH, index=False)

    metrics = {
        "model_version": "v2",
        "model_name": selection["v2"]["name"],
        "model_commit": "6428eb9abe8adfd9d9a19cd4df1eec7f4aa2737c",
        "mlflow_run_id": selection["v2"]["run_id"],
        "model_sha256": sha256_file(MODEL_PATH),
        "dataset_file": str(TEST_PATH.relative_to(ROOT)),
        "dataset_sha256": sha256_file(TEST_PATH),
        "rows": int(len(test)),
        "threshold": THRESHOLD,
        "score_attack_definition": "predict_proba column for class 1 (attack)",
        "positive_class": 1,
        "metrics": {
            "attack_recall": float(recall_score(y_true, predictions, pos_label=1, zero_division=0)),
            "attack_precision": float(precision_score(y_true, predictions, pos_label=1, zero_division=0)),
            "false_positive_rate": float(fp / (fp + tn)) if (fp + tn) else 0.0,
            "macro_f1": float(f1_score(y_true, predictions, average="macro", zero_division=0)),
        },
        "confusion_matrix_labels_0_1": matrix.tolist(),
        "prediction_columns": ["row_id", "y_true", "score_attack", "y_pred"],
        "test_used_for_model_selection": False,
    }
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"Predictions written to {PREDICTIONS_PATH}")
    print(f"Metrics written to {METRICS_PATH}")


if __name__ == "__main__":
    main()
