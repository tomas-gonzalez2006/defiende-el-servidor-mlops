"""Create a reproducible, group-aware train/validation split."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "UNSW_NB15_training-set.csv"
OUTPUT_DIR = ROOT / "data" / "processed"
EVIDENCE_DIR = ROOT / "evidencias"
SEED = 42
VALIDATION_SIZE = 0.2
TARGET = "label"
IDENTIFIERS = {"id", "attack_cat", TARGET}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not RAW_PATH.is_file():
        raise FileNotFoundError(f"Training CSV not found: {RAW_PATH}")

    frame = pd.read_csv(RAW_PATH, low_memory=False)
    required = {"id", "attack_cat", TARGET}
    missing_columns = required.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"Required columns are missing: {sorted(missing_columns)}")
    if frame["id"].duplicated().any():
        raise ValueError("The training CSV contains duplicate row identifiers.")
    if frame[TARGET].isna().any():
        raise ValueError("The target contains missing values.")

    predictors = [column for column in frame.columns if column not in IDENTIFIERS]
    predictor_hashes = pd.util.hash_pandas_object(
        frame[predictors], index=False
    ).to_numpy()
    train_positions, validation_positions = next(
        GroupShuffleSplit(
            n_splits=1,
            test_size=VALIDATION_SIZE,
            random_state=SEED,
        ).split(frame, groups=predictor_hashes)
    )

    training = frame.iloc[train_positions].copy()
    validation = frame.iloc[validation_positions].copy()
    training_hashes = set(predictor_hashes[train_positions].tolist())
    validation_hashes = set(predictor_hashes[validation_positions].tolist())
    overlapping_groups = training_hashes.intersection(validation_hashes)
    if overlapping_groups:
        raise RuntimeError(
            f"Group leakage detected: {len(overlapping_groups)} predictor groups overlap."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    train_path = OUTPUT_DIR / "train.csv"
    validation_path = OUTPUT_DIR / "validation.csv"
    assignment_path = OUTPUT_DIR / "split_assignment.csv"

    training.to_csv(train_path, index=False)
    validation.to_csv(validation_path, index=False)
    assignments = pd.DataFrame(
        {
            "id": frame["id"],
            "predictor_hash": predictor_hashes.astype(str),
            "split": "train",
        }
    )
    assignments.loc[validation_positions, "split"] = "validation"
    assignments.to_csv(assignment_path, index=False)

    summary = {
        "source_file": str(RAW_PATH.relative_to(ROOT)),
        "source_sha256": sha256_file(RAW_PATH),
        "seed": SEED,
        "method": "GroupShuffleSplit",
        "validation_fraction_requested": VALIDATION_SIZE,
        "group_columns": predictors,
        "group_definition": (
            "Exact predictor-row hash; excludes id, label, and attack_cat."
        ),
        "contradictory_label_policy": (
            "Retain every source row and its label; keep identical-predictor rows "
            "together in the same split."
        ),
        "target": TARGET,
        "features_excluded_from_model": sorted(IDENTIFIERS),
        "train": {
            "rows": int(len(training)),
            "groups": int(len(training_hashes)),
            "label_counts": {
                str(key): int(value)
                for key, value in training[TARGET].value_counts().sort_index().items()
            },
            "csv_sha256": sha256_file(train_path),
        },
        "validation": {
            "rows": int(len(validation)),
            "groups": int(len(validation_hashes)),
            "label_counts": {
                str(key): int(value)
                for key, value in validation[TARGET]
                .value_counts()
                .sort_index()
                .items()
            },
            "csv_sha256": sha256_file(validation_path),
        },
        "assignment_csv_sha256": sha256_file(assignment_path),
        "overlapping_predictor_groups": len(overlapping_groups),
        "test_data_used": False,
    }

    split_path = EVIDENCE_DIR / "splits.json"
    split_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Split evidence written to {split_path}")


if __name__ == "__main__":
    main()
