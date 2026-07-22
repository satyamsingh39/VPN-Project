import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from src.core.pipeline import PredictionPipeline
from src.config import FULL_DATASET_PATH

def main():
    print("=========================================")
    print("Initializing Hierarchical Pipeline Evaluation")
    print("=========================================\n")

    # Paths
    project_root = Path(__file__).resolve().parent
    dataset_path = FULL_DATASET_PATH
    results_dir = project_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Load Data
    print(f"Loading dataset from: {dataset_path}")
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {dataset_path}")
    
    df = pd.read_csv(dataset_path)
    if "traffic_type" not in df.columns:
        raise ValueError("Ground-truth column 'traffic_type' is missing from the dataset!")

    print(f"Loaded {len(df)} records.\n")

    # Initialize Pipeline
    print("Loading models and initializing pipeline...")
    pipeline = PredictionPipeline()
    print("Pipeline ready.\n")

    # Run Prediction
    print("Running batch predictions through the hierarchical pipeline...")
    # PredictionPipeline.predict() returns a DataFrame with all original + prediction columns
    pred_df = pipeline.predict(df)
    print("Inference completed.\n")

    # Step 3: Create Final Hierarchical Prediction
    print("Generating final hierarchical predictions...")
    final_preds = []
    for idx, row in pred_df.iterrows():
        t_type = row["Traffic Type"]
        app = row["Application"]
        if t_type == "VPN":
            final_preds.append(f"VPN-{app}")
        else:
            final_preds.append(app)
    pred_df["Final Prediction"] = final_preds

    # Step 4: Create Ground-Truth Traffic Type
    print("Deriving ground-truth traffic types...")
    pred_df["Actual Traffic Type"] = pred_df["traffic_type"].apply(
        lambda x: "VPN" if str(x).startswith("VPN-") else "Non-VPN"
    )

    # Step 7: Create Correct / Incorrect Column
    pred_df["Correct"] = pred_df["traffic_type"] == pred_df["Final Prediction"]

    # Step 5: Stage-1 VPN Detector Evaluation
    actual_t_type = pred_df["Actual Traffic Type"]
    pred_t_type = pred_df["Traffic Type"]

    vpn_acc = accuracy_score(actual_t_type, pred_t_type)
    vpn_prec = precision_score(actual_t_type, pred_t_type, pos_label="VPN", zero_division=0)
    vpn_rec = recall_score(actual_t_type, pred_t_type, pos_label="VPN", zero_division=0)
    vpn_f1 = f1_score(actual_t_type, pred_t_type, pos_label="VPN", zero_division=0)

    # Step 6: End-to-End Hierarchical Evaluation
    y_true = pred_df["traffic_type"]
    y_pred = pred_df["Final Prediction"]

    overall_acc = accuracy_score(y_true, y_pred)
    weighted_prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    weighted_rec = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    macro_prec = precision_score(y_true, y_pred, average="macro", zero_division=0)
    macro_rec = recall_score(y_true, y_pred, average="macro", zero_division=0)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

    correct_cnt = int(pred_df["Correct"].sum())
    incorrect_cnt = len(pred_df) - correct_cnt

    # Step 8: Print Clean Final Results
    print("============================================================")
    print("       HIERARCHICAL PIPELINE EVALUATION")
    print("============================================================")
    print(f"Total Samples                    : {len(df)}")
    print("------------------------------------------------------------")
    print("STAGE-1: VPN DETECTION")
    print("------------------------------------------------------------")
    print(f"Accuracy                         : {vpn_acc * 100:.2f}%")
    print(f"Precision                        : {vpn_prec * 100:.2f}%")
    print(f"Recall                           : {vpn_rec * 100:.2f}%")
    print(f"F1 Score                         : {vpn_f1 * 100:.2f}%")
    print("------------------------------------------------------------")
    print("END-TO-END HIERARCHICAL CLASSIFICATION")
    print("------------------------------------------------------------")
    print(f"Accuracy                         : {overall_acc * 100:.2f}%")
    print(f"Weighted Precision               : {weighted_prec * 100:.2f}%")
    print(f"Weighted Recall                  : {weighted_rec * 100:.2f}%")
    print(f"Weighted F1 Score                : {weighted_f1 * 100:.2f}%")
    print()
    print(f"Macro Precision                  : {macro_prec * 100:.2f}%")
    print(f"Macro Recall                     : {macro_rec * 100:.2f}%")
    print(f"Macro F1 Score                   : {macro_f1 * 100:.2f}%")
    print()
    print(f"Correct Predictions              : {correct_cnt}")
    print(f"Incorrect Predictions            : {incorrect_cnt}")
    print("============================================================\n")

    # Classification Report
    print("CLASSIFICATION REPORT\n")
    class_report_str = classification_report(y_true, y_pred, zero_division=0)
    print(class_report_str)

    # Step 9: Confusion Matrix
    print("Generating and saving confusion matrix...")
    labels = sorted(y_true.unique())
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels
    )
    plt.title("Hierarchical Classification Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    cm_path = results_dir / "hierarchical_confusion_matrix.png"
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"Confusion matrix saved to: {cm_path}\n")

    # Step 10: Save Row-Level Results
    eval_csv_path = results_dir / "hierarchical_evaluation.csv"
    pred_df.to_csv(eval_csv_path, index=False)
    print(f"Row-level evaluation results saved to: {eval_csv_path}\n")

    # Step 11: Save Metrics
    metrics_json_path = results_dir / "hierarchical_metrics.json"
    metrics_data = {
        "total_samples": len(df),
        "vpn_detection": {
            "accuracy": float(vpn_acc),
            "precision": float(vpn_prec),
            "recall": float(vpn_rec),
            "f1_score": float(vpn_f1)
        },
        "hierarchical_classification": {
            "accuracy": float(overall_acc),
            "weighted_precision": float(weighted_prec),
            "weighted_recall": float(weighted_rec),
            "weighted_f1": float(weighted_f1),
            "macro_precision": float(macro_prec),
            "macro_recall": float(macro_rec),
            "macro_f1": float(macro_f1),
            "correct_predictions": int(correct_cnt),
            "incorrect_predictions": int(incorrect_cnt)
        }
    }
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=4)
    print(f"Metrics JSON saved to: {metrics_json_path}\n")

    # Warning
    print("IMPORTANT:")
    print("This evaluation was performed on datasets/dataset.csv.")
    print("If this dataset contains samples used during model training,")
    print("these results should not be reported as unbiased test-set performance.")
    print("For research reporting, evaluate the complete hierarchical pipeline")
    print("on a completely unseen held-out test dataset.\n")

if __name__ == "__main__":
    main()
