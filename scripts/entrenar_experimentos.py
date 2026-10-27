"""Train four baseline configurations and log validation results to MLflow."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import mlflow
import mlflow.sklearn
import joblib
import pandas as pd
from mlflow.tracking import MlflowClient
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = ROOT / "data" / "processed" / "train.csv"
VALIDATION_PATH = ROOT / "data" / "processed" / "validation.csv"
SPLIT_METADATA_PATH = ROOT / "evidencias" / "splits.json"
SUMMARY_PATH = ROOT / "evidencias" / "experimentos.csv"
EVIDENCE_DIR = ROOT / "evidencias" / "mlflow"
TARGET = "label"
EXCLUDED = {"id", "attack_cat", TARGET}
SEED = 42
THRESHOLD = 0.5
EXPERIMENT_NAME = "UNSW-NB15-baselines"
LOCAL_TRACKING_DIR = (
    Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    / "DefiendeElServidor"
    / "mlflow"
)
TRACKING_DATABASE = LOCAL_TRACKING_DIR / "mlflow.db"
ARTIFACTS_DIR = LOCAL_TRACKING_DIR / "artifacts"
TRACKING_URI = os.environ.get(
    "MLFLOW_TRACKING_URI",
    f"sqlite:///{TRACKING_DATABASE.resolve().as_posix()}",
)

CONFIGURATIONS = [
    {
        "name": "logistic_regression_c_0_1",
        "family": "logistic_regression",
        "hypothesis": (
            "La regresión logística con regularización más fuerte ofrece una "
            "referencia lineal estable."
        ),
        "parameters": {"C": 0.1, "max_iter": 300, "solver": "liblinear"},
    },
    {
        "name": "logistic_regression_c_1",
        "family": "logistic_regression",
        "hypothesis": (
            "Reducir la regularización respecto a C=0.1 puede mejorar el ajuste "
            "sin cambiar la familia del modelo."
        ),
        "parameters": {"C": 1.0, "max_iter": 300, "solver": "liblinear"},
    },
    {
        "name": "decision_tree_depth_12",
        "family": "decision_tree",
        "hypothesis": (
            "Un árbol de profundidad limitada puede capturar interacciones no "
            "lineales con una complejidad controlada."
        ),
        "parameters": {"max_depth": 12, "min_samples_leaf": 20},
    },
    {
        "name": "random_forest_100",
        "family": "random_forest",
        "hypothesis": (
            "Un ensamble de árboles puede reducir la varianza frente a un árbol "
            "individual."
        ),
        "parameters": {
            "n_estimators": 100,
            "max_depth": 20,
            "min_samples_leaf": 10,
            "n_jobs": -1,
        },
    },
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_revision() -> tuple[str, str]:
    git_executable = shutil.which("git")
    code_hash = sha256_file(Path(__file__))
    if git_executable is None:
        return "uncommitted", code_hash

    result = subprocess.run(
        [git_executable, "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip(), code_hash
    return "uncommitted", code_hash


def make_model(
    family: str,
    parameters: dict,
    numeric_features: list[str],
    categorical_features: list[str],
) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(with_mean=False), numeric_features),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=True),
                categorical_features,
            ),
        ],
        remainder="drop",
    )

    if family == "logistic_regression":
        estimator = LogisticRegression(
            **parameters,
            random_state=SEED,
        )
    elif family == "decision_tree":
        estimator = DecisionTreeClassifier(
            **parameters,
            random_state=SEED,
        )
    elif family == "random_forest":
        estimator = RandomForestClassifier(
            **parameters,
            random_state=SEED,
        )
    else:
        raise ValueError(f"Unsupported model family: {family}")

    return Pipeline(
        [
            ("preprocessing", preprocessor),
            ("estimator", estimator),
        ]
    )


def evaluate(y_true: pd.Series, y_score: pd.Series) -> tuple[dict, list[list[int]]]:
    y_pred = (y_score >= THRESHOLD).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    negative_count = tn + fp
    metrics = {
        "attack_recall": float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "attack_precision": float(
            precision_score(y_true, y_pred, pos_label=1, zero_division=0)
        ),
        "false_positive_rate": float(fp / negative_count) if negative_count else 0.0,
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "threshold": THRESHOLD,
        "validation_rows": int(len(y_true)),
        "confusion_tn": int(tn),
        "confusion_fp": int(fp),
        "confusion_fn": int(fn),
        "confusion_tp": int(tp),
    }
    return metrics, [[int(tn), int(fp)], [int(fn), int(tp)]]


def main() -> None:
    if not TRAIN_PATH.is_file() or not VALIDATION_PATH.is_file():
        raise FileNotFoundError(
            "Run `python scripts/crear_splits.py` before training experiments."
        )
    if not SPLIT_METADATA_PATH.is_file():
        raise FileNotFoundError(f"Split metadata not found: {SPLIT_METADATA_PATH}")

    train = pd.read_csv(TRAIN_PATH, low_memory=False)
    validation = pd.read_csv(VALIDATION_PATH, low_memory=False)
    split_metadata = json.loads(SPLIT_METADATA_PATH.read_text(encoding="utf-8"))
    if train.columns.tolist() != validation.columns.tolist():
        raise ValueError("Training and validation schemas do not match.")
    if TARGET not in train or train[TARGET].isna().any() or validation[TARGET].isna().any():
        raise ValueError("Training and validation must contain non-null targets.")

    features = [column for column in train.columns if column not in EXCLUDED]
    if not features:
        raise ValueError("No predictor features remain after excluding target and IDs.")
    train_x = train[features]
    validation_x = validation[features]
    train_y = train[TARGET]
    validation_y = validation[TARGET]
    numeric_features = train_x.select_dtypes(include="number").columns.tolist()
    categorical_features = [
        column for column in features if column not in numeric_features
    ]

    commit, code_sha256 = source_revision()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient(tracking_uri=TRACKING_URI)
    if client.get_experiment_by_name(EXPERIMENT_NAME) is None:
        client.create_experiment(
            EXPERIMENT_NAME,
            artifact_location=ARTIFACTS_DIR.resolve().as_uri(),
        )
    mlflow.set_experiment(EXPERIMENT_NAME)
    results: list[dict] = []
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        raise RuntimeError(f"MLflow experiment was not created: {EXPERIMENT_NAME}")
    completed_runs = client.search_runs(
        [experiment.experiment_id],
        filter_string="attributes.status = 'FINISHED'",
        max_results=1000,
    )
    completed_by_name = {
        run.data.tags.get("mlflow.runName"): run for run in completed_runs
    }

    for configuration in CONFIGURATIONS:
        previous_run = completed_by_name.get(configuration["name"])
        if previous_run is not None:
            previous_metrics_path = (
                EVIDENCE_DIR
                / previous_run.info.run_id
                / "validation_metrics.json"
            )
            if previous_metrics_path.is_file():
                previous_evidence = json.loads(
                    previous_metrics_path.read_text(encoding="utf-8")
                )
                previous_metrics = previous_evidence["metrics"]
                previous_matrix = previous_evidence["confusion_matrix_labels_0_1"]
                results.append(
                    {
                        "run_id": previous_run.info.run_id,
                        "model": configuration["name"],
                        "family": configuration["family"],
                        "hypothesis": configuration["hypothesis"],
                        "parameters": json.dumps(
                            configuration["parameters"], sort_keys=True
                        ),
                        "seed": SEED,
                        "code_git_commit": previous_run.data.params.get(
                            "code_git_commit", "unknown"
                        ),
                        "code_sha256": previous_run.data.params.get(
                            "code_sha256", "unknown"
                        ),
                        "training_sha256": previous_run.data.params.get(
                            "data_train_sha256", "unknown"
                        ),
                        "validation_sha256": previous_run.data.params.get(
                            "data_validation_sha256", "unknown"
                        ),
                        "model_uri": f"runs:/{previous_run.info.run_id}/complete_pipeline",
                        "workspace_model": str(
                            (
                                EVIDENCE_DIR
                                / previous_run.info.run_id
                                / "complete_pipeline.joblib"
                            ).relative_to(ROOT)
                        ),
                        **previous_metrics,
                        "confusion_matrix_0_1": json.dumps(previous_matrix),
                        "mlflow_run_url": (
                            "http://127.0.0.1:5000/#/experiments/"
                            f"{experiment.experiment_id}/runs/{previous_run.info.run_id}"
                        ),
                    }
                )
                print(
                    f"Reusing completed run {configuration['name']}: "
                    f"run_id={previous_run.info.run_id}"
                )
                continue

        model = make_model(
            configuration["family"],
            configuration["parameters"],
            numeric_features,
            categorical_features,
        )
        with mlflow.start_run(run_name=configuration["name"]) as run:
            mlflow.log_params(configuration["parameters"])
            mlflow.log_params(
                {
                    "family": configuration["family"],
                    "seed": SEED,
                    "threshold": THRESHOLD,
                    "validation_fraction": split_metadata[
                        "validation_fraction_requested"
                    ],
                    "split_method": split_metadata["method"],
                    "positive_class": 1,
                    "preprocessing": "StandardScaler + OneHotEncoder(handle_unknown=ignore)",
                }
            )
            mlflow.log_param("hypothesis", configuration["hypothesis"])
            mlflow.log_param("code_git_commit", commit)
            mlflow.log_param("code_sha256", code_sha256)
            mlflow.log_param(
                "data_train_sha256",
                split_metadata["train"]["csv_sha256"],
            )
            mlflow.log_param(
                "data_validation_sha256",
                split_metadata["validation"]["csv_sha256"],
            )
            mlflow.log_param("data_split_source_sha256", split_metadata["source_sha256"])

            model.fit(train_x, train_y)
            positive_index = list(model.classes_).index(1)
            probabilities = model.predict_proba(validation_x)[:, positive_index]
            metrics, matrix = evaluate(validation_y, pd.Series(probabilities))
            mlflow.log_metrics(
                {
                    key: value
                    for key, value in metrics.items()
                    if isinstance(value, (int, float))
                }
            )
            mlflow.log_dict(
                {
                    "run_id": run.info.run_id,
                    "model": configuration["name"],
                    "hypothesis": configuration["hypothesis"],
                    "positive_class": 1,
                    "threshold_rule": "predict attack if P(label=1) >= 0.5",
                    "confusion_matrix_labels_0_1": matrix,
                    "metrics": metrics,
                    "denominator_policy": (
                        "Precision/recall/F1 use zero_division=0; FPR=0 when "
                        "there are no negative validation examples."
                    ),
                },
                "validation_metrics.json",
            )
            model_info = mlflow.sklearn.log_model(
                model,
                name="complete_pipeline",
                input_example=train_x.head(5),
                signature=infer_signature(train_x.head(5), model.predict(train_x.head(5))),
                skops_trusted_types=(
                    ["sklearn.tree._tree.Tree"]
                    if configuration["family"]
                    in {"decision_tree", "random_forest"}
                    else None
                ),
            )
            run_evidence_dir = EVIDENCE_DIR / run.info.run_id
            run_evidence_dir.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, run_evidence_dir / "complete_pipeline.joblib")
            (run_evidence_dir / "validation_metrics.json").write_text(
                json.dumps(
                    {
                        "run_id": run.info.run_id,
                        "model": configuration["name"],
                        "family": configuration["family"],
                        "hypothesis": configuration["hypothesis"],
                        "parameters": configuration["parameters"],
                        "positive_class": 1,
                        "threshold_rule": "predict attack if P(label=1) >= 0.5",
                        "confusion_matrix_labels_0_1": matrix,
                        "metrics": metrics,
                        "denominator_policy": (
                            "Precision/recall/F1 use zero_division=0; FPR=0 when "
                            "there are no negative validation examples."
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = {
                "run_id": run.info.run_id,
                "model": configuration["name"],
                "family": configuration["family"],
                "hypothesis": configuration["hypothesis"],
                "parameters": json.dumps(configuration["parameters"], sort_keys=True),
                "seed": SEED,
                "code_git_commit": commit,
                "code_sha256": code_sha256,
                "training_sha256": split_metadata["train"]["csv_sha256"],
                "validation_sha256": split_metadata["validation"]["csv_sha256"],
                "model_uri": model_info.model_uri,
                "workspace_model": str(
                    (run_evidence_dir / "complete_pipeline.joblib").relative_to(ROOT)
                ),
                **metrics,
                "confusion_matrix_0_1": json.dumps(matrix),
                "mlflow_run_url": (
                    "http://127.0.0.1:5000/#/experiments/"
                    f"{run.info.experiment_id}/runs/{run.info.run_id}"
                ),
            }
            results.append(result)
            print(
                f"Completed {configuration['name']}: run_id={run.info.run_id}, "
                f"recall={metrics['attack_recall']:.4f}, "
                f"precision={metrics['attack_precision']:.4f}, "
                f"FPR={metrics['false_positive_rate']:.4f}, "
                f"macro_f1={metrics['macro_f1']:.4f}"
            )

    results_frame = pd.DataFrame(results)
    results_frame.to_csv(SUMMARY_PATH, index=False)
    print(f"Experiment summary written to {SUMMARY_PATH}")
    print(f"MLflow tracking URI: {TRACKING_URI}")
    print("MLflow UI (when started): http://127.0.0.1:5000")


if __name__ == "__main__":
    main()
