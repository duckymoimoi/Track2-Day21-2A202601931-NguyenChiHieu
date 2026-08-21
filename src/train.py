import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
import json
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

EVAL_THRESHOLD = 0.70

# Use the local SQLite backend by default while still allowing CI or a remote
# tracking server to override it through the standard MLflow environment var.
mlflow.set_tracking_uri(
    os.getenv("MLFLOW_TRACKING_URI") or "sqlite:///mlflow.db"
)


def build_model(params: dict):
    """Build one of the bonus model families from flat or nested parameters."""
    model_type = params.get("model_type", "random_forest")
    nested_params = params.get(model_type)
    if isinstance(nested_params, dict):
        model_params = nested_params.copy()
    else:
        model_params = {
            key: value
            for key, value in params.items()
            if key != "model_type" and not isinstance(value, dict)
        }

    if model_type == "random_forest":
        return (
            RandomForestClassifier(
                **model_params,
                random_state=42,
                n_jobs=-1,
            ),
            model_type,
            model_params,
        )
    if model_type == "gradient_boosting":
        return (
            GradientBoostingClassifier(**model_params, random_state=42),
            model_type,
            model_params,
        )
    if model_type == "logistic_regression":
        model_params.setdefault("max_iter", 2000)
        return (
            Pipeline(
                [
                    ("scale", StandardScaler()),
                    (
                        "model",
                        LogisticRegression(**model_params, random_state=42),
                    ),
                ]
            ),
            model_type,
            model_params,
        )
    raise ValueError(f"Unsupported model_type: {model_type}")


def train(
    params: dict,
    data_path: str = "data/train_phase1.csv",
    eval_path: str = "data/eval.csv",
) -> float:
    """
    Huan luyen mo hinh va ghi nhan ket qua vao MLflow.

    Tham so:
        params     : dict chua cac sieu tham so cho RandomForestClassifier.
        data_path  : duong dan den file du lieu huan luyen.
        eval_path  : duong dan den file du lieu danh gia.

    Tra ve:
        accuracy (float): do chinh xac tren tap danh gia.
    """

    df_train = pd.read_csv(data_path)
    df_eval = pd.read_csv(eval_path)

    X_train = df_train.drop(columns=["target"])
    y_train = df_train["target"]
    X_eval = df_eval.drop(columns=["target"])
    y_eval = df_eval["target"]

    model, model_type, model_params = build_model(params)
    run_name = f"{model_type}-" + "-".join(
        f"{key}={value}" for key, value in sorted(model_params.items())
    )
    with mlflow.start_run(run_name=run_name):

        mlflow.log_params({"model_type": model_type, **model_params})
        mlflow.set_tag("training_data", os.path.basename(data_path))

        model.fit(X_train, y_train)

        preds = model.predict(X_eval)
        acc = float(accuracy_score(y_eval, preds))
        f1 = float(f1_score(y_eval, preds, average="weighted"))
        class_names = ["thap", "trung_binh", "cao"]
        per_class = classification_report(
            y_eval,
            preds,
            labels=[0, 1, 2],
            target_names=class_names,
            output_dict=True,
            zero_division=0,
        )
        matrix = confusion_matrix(y_eval, preds, labels=[0, 1, 2])

        label_distribution = (
            y_train.value_counts(normalize=True).sort_index().to_dict()
        )
        label_distribution = {
            str(label): float(label_distribution.get(label, 0.0))
            for label in [0, 1, 2]
        }
        for label, ratio in label_distribution.items():
            if ratio < 0.10:
                print(
                    f"WARNING: class {label} represents only {ratio:.2%} "
                    "of training data."
                )

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        for class_name in class_names:
            mlflow.log_metric(
                f"precision_{class_name}", per_class[class_name]["precision"]
            )
            mlflow.log_metric(
                f"recall_{class_name}", per_class[class_name]["recall"]
            )
        mlflow.sklearn.log_model(model, "model")

        print(f"Accuracy: {acc:.4f} | F1: {f1:.4f}")

        os.makedirs("outputs", exist_ok=True)
        metrics = {
            "model_type": model_type,
            "accuracy": acc,
            "f1_score": f1,
            "training_samples": int(len(df_train)),
            "eval_samples": int(len(df_eval)),
            "label_distribution": label_distribution,
            "precision": {
                name: float(per_class[name]["precision"])
                for name in class_names
            },
            "recall": {
                name: float(per_class[name]["recall"])
                for name in class_names
            },
            "confusion_matrix": matrix.tolist(),
        }
        with open("outputs/metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)

        with open("outputs/report.txt", "w") as f:
            f.write(f"Model: {model_type}\n")
            f.write(f"Training samples: {len(df_train)}\n")
            f.write(f"Accuracy: {acc:.4f}\n")
            f.write(f"Weighted F1: {f1:.4f}\n\n")
            f.write("Confusion matrix (rows=true, columns=predicted):\n")
            f.write(f"{matrix}\n\n")
            f.write("Per-class report:\n")
            f.write(
                classification_report(
                    y_eval,
                    preds,
                    labels=[0, 1, 2],
                    target_names=class_names,
                    zero_division=0,
                )
            )
            f.write("\nTraining label distribution:\n")
            for label, ratio in label_distribution.items():
                f.write(f"class {label}: {ratio:.4%}\n")

        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")

    return acc


if __name__ == "__main__":
    with open("params.yaml") as f:
        params = yaml.safe_load(f)
    train(params)
