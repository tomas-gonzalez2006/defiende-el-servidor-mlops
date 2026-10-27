"""Audit the published UNSW-NB15 partitions and write a compact EDA."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
EVIDENCE_DIR = ROOT / "evidencias"
FILES = {
    "training": {
        "name": "UNSW_NB15_training-set.csv",
        "rows": 175_341,
        "sha256": "bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa",
        "url": (
            "https://raw.githubusercontent.com/Nir-J/ML-Projects/"
            "44bbd02b9e70f74dd915218d5eb702f125341ffc/"
            "UNSW-Network_Packet_Classification/UNSW_NB15_training-set.csv"
        ),
    },
    "testing": {
        "name": "UNSW_NB15_testing-set.csv",
        "rows": 82_332,
        "sha256": "734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559",
        "url": (
            "https://raw.githubusercontent.com/Nir-J/ML-Projects/"
            "44bbd02b9e70f74dd915218d5eb702f125341ffc/"
            "UNSW-Network_Packet_Classification/UNSW_NB15_testing-set.csv"
        ),
    },
}
OFFICIAL_SOURCE = "https://research.unsw.edu.au/projects/unsw-nb15-dataset"
EXCLUDED_PREDICTORS = {"id", "label", "attack_cat"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def label_counts(frame: pd.DataFrame) -> dict[str, dict[str, float | int]]:
    counts = frame["label"].value_counts(dropna=False).sort_index()
    return {
        str(label): {
            "count": int(count),
            "proportion": float(count / len(frame)),
        }
        for label, count in counts.items()
    }


def audit_frame(frame: pd.DataFrame, path: Path, metadata: dict) -> dict:
    predictors = [column for column in frame.columns if column not in EXCLUDED_PREDICTORS]
    duplicate_mask = frame.duplicated(subset=predictors, keep=False)
    duplicate_groups = frame.loc[duplicate_mask].groupby(
        predictors, dropna=False, sort=False
    )["label"].nunique()
    contradictory_groups = duplicate_groups[duplicate_groups > 1]

    return {
        "file": metadata["name"],
        "source_url": metadata["url"],
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "expected_sha256": metadata["sha256"],
        "sha256_matches_expected_mirror": sha256_file(path) == metadata["sha256"],
        "rows": int(len(frame)),
        "expected_rows": metadata["rows"],
        "columns": int(len(frame.columns)),
        "column_names": frame.columns.tolist(),
        "column_types": {column: str(dtype) for column, dtype in frame.dtypes.items()},
        "type_counts": {
            str(dtype): int(count)
            for dtype, count in frame.dtypes.astype(str).value_counts().items()
        },
        "missing_values_total": int(frame.isna().sum().sum()),
        "missing_values_by_column": {
            column: int(count)
            for column, count in frame.isna().sum().items()
            if count
        },
        "label_counts": label_counts(frame),
        "attack_category_counts": {
            str(category): int(count)
            for category, count in frame["attack_cat"]
            .value_counts(dropna=False)
            .items()
        },
        "exact_full_row_duplicates": int(frame.duplicated().sum()),
        "predictor_columns_for_duplicate_audit": predictors,
        "duplicate_predictor_rows_after_first": int(
            frame.duplicated(subset=predictors).sum()
        ),
        "rows_in_duplicate_predictor_groups": int(duplicate_mask.sum()),
        "contradictory_predictor_groups": int(len(contradictory_groups)),
        "rows_in_contradictory_predictor_groups": int(
            contradictory_groups.sum()
        ),
    }


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    frames: dict[str, pd.DataFrame] = {}
    audits: dict[str, dict] = {}

    for split, metadata in FILES.items():
        path = RAW_DIR / metadata["name"]
        if not path.is_file():
            raise FileNotFoundError(f"Dataset file not found: {path}")

        actual_hash = sha256_file(path)
        if actual_hash != metadata["sha256"]:
            raise ValueError(
                f"SHA-256 mismatch for {metadata['name']}: {actual_hash}"
            )

        frame = pd.read_csv(path, low_memory=False)
        if len(frame) != metadata["rows"]:
            raise ValueError(
                f"Unexpected row count for {metadata['name']}: {len(frame)}"
            )
        if not {"id", "label", "attack_cat"}.issubset(frame.columns):
            raise ValueError(f"Required columns are missing from {metadata['name']}")

        frames[split] = frame
        audits[split] = audit_frame(frame, path, metadata)

    training = frames["training"]
    testing = frames["testing"]
    if training.columns.tolist() != testing.columns.tolist():
        raise ValueError("Training and testing schemas do not match")

    predictors = [
        column for column in training.columns if column not in EXCLUDED_PREDICTORS
    ]
    train_keys = set(
        pd.util.hash_pandas_object(training[predictors], index=False).tolist()
    )
    test_keys = pd.util.hash_pandas_object(testing[predictors], index=False)
    overlap_rows = int(test_keys.isin(train_keys).sum())
    audits["cross_split_predictor_overlap"] = {
        "method": "pandas row hashes over predictors; excludes id, label, attack_cat",
        "test_rows_matching_a_training_predictor_row": overlap_rows,
        "test_rows": int(len(testing)),
        "test_overlap_proportion": float(overlap_rows / len(testing)),
        "distinct_training_predictor_rows": int(
            pd.util.hash_pandas_object(training[predictors], index=False).nunique()
        ),
        "distinct_testing_predictor_rows": int(test_keys.nunique()),
        "note": (
            "Descriptive audit only. Test labels were not used for modeling "
            "or selection."
        ),
    }
    audits["provenance"] = {
        "download_date": date.today().isoformat(),
        "official_attribution_source": OFFICIAL_SOURCE,
        "download_source": "Third-party mirror pinned to commit 44bbd02b9e70f74dd915218d5eb702f125341ffc",
        "mirror_hashes_are_not_authentication_of_the_official_source": True,
    }

    audit_path = EVIDENCE_DIR / "auditoria_datos.json"
    audit_path.write_text(
        json.dumps(audits, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_eda(training, testing, audits)
    print(f"Audit written to {audit_path}")
    print(f"EDA written to {EVIDENCE_DIR / 'eda_rapido.md'}")
    print(f"Chart written to {EVIDENCE_DIR / 'eda_distribucion.png'}")


def write_eda(training: pd.DataFrame, testing: pd.DataFrame, audits: dict) -> None:
    train_labels = label_counts(training)
    test_labels = label_counts(testing)
    top_categories = (
        training["attack_cat"].value_counts().rename("train")
        .to_frame()
        .join(testing["attack_cat"].value_counts().rename("test"), how="outer")
        .fillna(0)
        .astype(int)
    )
    categorical = {}
    for column in ("proto", "service", "state"):
        categorical[column] = {
            split: frame[column].value_counts().head(5).to_dict()
            for split, frame in (("training", training), ("testing", testing))
        }

    numeric_features = [
        column
        for column in training.select_dtypes(include="number").columns
        if column not in {"id", "label"}
    ]
    numeric_summary = (
        training[numeric_features]
        .quantile([0.0, 0.5, 0.75, 0.95, 1.0])
        .round(4)
        .T
    )

    lines = [
        "# EDA rápido — UNSW-NB15",
        "",
        f"Fecha de auditoría: {audits['provenance']['download_date']}.",
        "",
        "## Integridad y esquema",
        "",
        "| Partición | Filas | Columnas | SHA-256 verificado | Nulos |",
        "|---|---:|---:|---|---:|",
    ]
    for split in ("training", "testing"):
        item = audits[split]
        lines.append(
            f"| {item['file']} | {item['rows']:,} | {item['columns']} | "
            f"{'sí' if item['sha256_matches_expected_mirror'] else 'no'} | "
            f"{item['missing_values_total']:,} |"
        )
    lines.extend(
        [
            "",
            "Las dos particiones comparten esquema y contienen 45 columnas "
            "(30 enteras, 11 flotantes y 4 de texto).",
            "",
            "## Variable objetivo",
            "",
            "| Partición | Normal (0) | Ataque (1) | Proporción de ataques |",
            "|---|---:|---:|---:|",
        ]
    )
    for split, labels in (("training", train_labels), ("testing", test_labels)):
        lines.append(
            f"| {split} | {labels['0']['count']:,} ({labels['0']['proportion']:.1%}) | "
            f"{labels['1']['count']:,} ({labels['1']['proportion']:.1%}) | "
            f"{labels['1']['proportion']:.1%} |"
        )

    lines.extend(
        [
            "",
            "La proporción de ataques difiere entre entrenamiento y test; "
            "consérvese como observación de distribución, no como criterio "
            "para ajustar el modelo con test.",
            "",
            "## Categorías de ataque",
            "",
            "| Categoría | Entrenamiento | Test |",
            "|---|---:|---:|",
        ]
    )
    for category, row in top_categories.sort_values("train", ascending=False).iterrows():
        lines.append(f"| {category} | {row['train']:,} | {row['test']:,} |")

    lines.extend(["", "## Variables categóricas frecuentes", ""])
    for column, split_values in categorical.items():
        lines.append(f"### `{column}`")
        lines.append("")
        for split, counts in split_values.items():
            values = ", ".join(f"`{value}`: {count:,}" for value, count in counts.items())
            lines.append(f"- {split}: {values}")
        lines.append("")

    lines.extend(
        [
            "## Duplicados y solapamiento",
            "",
            "| Partición | Filas repetidas por predictores tras la primera | "
            "Grupos con etiquetas contradictorias |",
            "|---|---:|---:|",
        ]
    )
    for split in ("training", "testing"):
        item = audits[split]
        lines.append(
            f"| {split} | {item['duplicate_predictor_rows_after_first']:,} | "
            f"{item['contradictory_predictor_groups']:,} |"
        )
    overlap = audits["cross_split_predictor_overlap"]
    lines.extend(
        [
            "",
            f"Hay {overlap['test_rows_matching_a_training_predictor_row']:,} de "
            f"{overlap['test_rows']:,} filas de test "
            f"({overlap['test_overlap_proportion']:.2%}) cuyo vector de "
            "predictores aparece también en entrenamiento. El cotejo excluye "
            "`id`, `label` y `attack_cat`.",
            "",
            "Los grupos de predictores duplicados con etiquetas contradictorias "
            "requieren una política documentada antes de crear entrenamiento/"
            "validación. No se eliminan ni se resuelven automáticamente en este "
            "EDA. Al crear la validación desde entrenamiento, mantén cada grupo "
            "de predictores en una sola partición.",
            "",
            "## Resumen numérico de entrenamiento",
            "",
            "Cuantiles de las variables numéricas (sin `id` ni `label`):",
            "",
            "| Variable | Mín. | Mediana | P75 | P95 | Máx. |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for column, values in numeric_summary.iterrows():
        lines.append(
            f"| `{column}` | {values.iloc[0]:g} | {values.iloc[1]:g} | "
            f"{values.iloc[2]:g} | {values.iloc[3]:g} | {values.iloc[4]:g} |"
        )
    lines.extend(
        [
            "",
            "## Alcance y cautelas",
            "",
            "- El objetivo para el modelo es `label`; excluye `label`, `attack_cat` "
            "e `id` de las entradas. `attack_cat` revela la respuesta e `id` "
            "sirve solo para auditoría y trazabilidad.",
            "- No se han creado aquí particiones de validación ni transformaciones.",
            "- El análisis del test se limita a auditoría descriptiva; sus etiquetas "
            "y métricas no deben guiar la elección del modelo o del umbral.",
            "- Fuente de atribución oficial: "
            f"[UNSW-NB15]({OFFICIAL_SOURCE}). Descarga usada: mirror de terceros "
            "fijado en un commit; las huellas SHA-256 verifican la copia del "
            "mirror, no la autenticidad del origen oficial.",
            "",
            "La auditoría completa por columna, tipo y huella está en "
            "`auditoria_datos.json`.",
        ]
    )
    (EVIDENCE_DIR / "eda_rapido.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    categories = top_categories.index.tolist()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    labels = ["Normal (0)", "Ataque (1)"]
    train_values = [train_labels["0"]["count"], train_labels["1"]["count"]]
    test_values = [test_labels["0"]["count"], test_labels["1"]["count"]]
    x = range(len(labels))
    width = 0.36
    axes[0].bar([i - width / 2 for i in x], train_values, width, label="Entrenamiento")
    axes[0].bar([i + width / 2 for i in x], test_values, width, label="Test")
    axes[0].set_xticks(list(x), labels)
    axes[0].set_title("Clase binaria")
    axes[0].set_ylabel("Filas")
    axes[0].legend()

    category_positions = range(len(categories))
    axes[1].barh(
        [position - width / 2 for position in category_positions],
        top_categories["train"],
        width,
        label="Entrenamiento",
    )
    axes[1].barh(
        [position + width / 2 for position in category_positions],
        top_categories["test"],
        width,
        label="Test",
    )
    axes[1].set_yticks(list(category_positions), categories)
    axes[1].set_title("Categoría de ataque")
    axes[1].set_xlabel("Filas")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(EVIDENCE_DIR / "eda_distribucion.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
