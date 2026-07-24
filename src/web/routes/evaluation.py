"""
Evaluation routes blueprint — Hierarchical model evaluation analytics & interactive metrics.
"""
from pathlib import Path
import json
import pandas as pd
import numpy as np
from flask import Blueprint, render_template, current_app, jsonify
from sklearn.metrics import classification_report, confusion_matrix

from src.config import PROJECT_ROOT

evaluation_bp = Blueprint("evaluation", __name__)

_EVAL_CACHE = None

def get_evaluation_data():
    """
    Loads and processes hierarchical_metrics.json & hierarchical_evaluation.csv.
    Caches the calculated metrics dictionary in memory.
    """
    global _EVAL_CACHE
    if _EVAL_CACHE is not None:
        return _EVAL_CACHE

    results_dir = PROJECT_ROOT / "results"
    metrics_path = results_dir / "hierarchical_metrics.json"
    csv_path = results_dir / "hierarchical_evaluation.csv"

    if not metrics_path.exists() or not csv_path.exists():
        return None

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_json = json.load(f)

    df = pd.read_csv(csv_path)

    # 1. Unique classes sorted
    all_classes = sorted(list(set(df["traffic_type"].unique()).union(set(df["Final Prediction"].unique()))))

    # 2. Confusion Matrix Calculation
    cm = confusion_matrix(df["traffic_type"], df["Final Prediction"], labels=all_classes)
    cm_list = cm.tolist()

    # 3. Per-class metrics
    report = classification_report(
        df["traffic_type"],
        df["Final Prediction"],
        labels=all_classes,
        output_dict=True,
        zero_division=0
    )

    per_class_metrics = []
    for cls in all_classes:
        if cls in report:
            item = report[cls]
            per_class_metrics.append({
                "class_name": cls,
                "precision": round(float(item["precision"]), 4),
                "recall": round(float(item["recall"]), 4),
                "f1_score": round(float(item["f1-score"]), 4),
                "support": int(item["support"])
            })

    # Sort classes by F1
    sorted_by_f1 = sorted(per_class_metrics, key=lambda x: x["f1_score"], reverse=True)
    strongest_classes = sorted_by_f1[:3]
    weakest_classes = sorted_by_f1[-3:][::-1]

    sorted_by_recall = sorted(per_class_metrics, key=lambda x: x["recall"])
    lowest_recall_classes = sorted_by_recall[:3]

    # 4. Top Misclassifications (Confusion Pairs)
    incorrect_df = df[df["traffic_type"] != df["Final Prediction"]]
    misclass_counts = (
        incorrect_df.groupby(["traffic_type", "Final Prediction"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    top_misclassifications = []
    for _, row in misclass_counts.head(10).iterrows():
        top_misclassifications.append({
            "actual": str(row["traffic_type"]),
            "predicted": str(row["Final Prediction"]),
            "count": int(row["count"])
        })

    # 5. Stage-Level Error Analysis
    total_samples = len(df)
    stage1_errors = int((df["Actual Traffic Type"] != df["Traffic Type"]).sum())
    stage2_errors = int(((df["Actual Traffic Type"] == df["Traffic Type"]) & (~df["Correct"])).sum())
    total_errors = int((~df["Correct"]).sum())

    stage_error_analysis = {
        "total_samples": total_samples,
        "total_errors": total_errors,
        "stage1_errors": stage1_errors,
        "stage1_error_pct": round(stage1_errors / total_samples * 100, 2),
        "stage2_errors": stage2_errors,
        "stage2_error_pct": round(stage2_errors / total_samples * 100, 2),
    }

    # 6. Confidence Score Analysis
    correct_mask = df["Correct"] == True
    incorrect_mask = df["Correct"] == False

    t_conf_correct = df.loc[correct_mask, "Traffic Confidence"].round(4).tolist()
    t_conf_incorrect = df.loc[incorrect_mask, "Traffic Confidence"].round(4).tolist()

    a_conf_correct = df.loc[correct_mask, "Application Confidence"].round(4).tolist()
    a_conf_incorrect = df.loc[incorrect_mask, "Application Confidence"].round(4).tolist()

    confidence_analysis = {
        "traffic_conf_correct": t_conf_correct,
        "traffic_conf_incorrect": t_conf_incorrect,
        "app_conf_correct": a_conf_correct,
        "app_conf_incorrect": a_conf_incorrect,
        "avg_traffic_conf_correct": round(float(df.loc[correct_mask, "Traffic Confidence"].mean()), 4),
        "avg_traffic_conf_incorrect": round(float(df.loc[incorrect_mask, "Traffic Confidence"].mean()), 4),
        "avg_app_conf_correct": round(float(df.loc[correct_mask, "Application Confidence"].mean()), 4),
        "avg_app_conf_incorrect": round(float(df.loc[incorrect_mask, "Application Confidence"].mean()), 4),
    }

    _EVAL_CACHE = {
        "summary": metrics_json,
        "all_classes": all_classes,
        "confusion_matrix": cm_list,
        "per_class_metrics": per_class_metrics,
        "strongest_classes": strongest_classes,
        "weakest_classes": weakest_classes,
        "lowest_recall_classes": lowest_recall_classes,
        "top_misclassifications": top_misclassifications,
        "stage_error_analysis": stage_error_analysis,
        "confidence_analysis": confidence_analysis
    }

    return _EVAL_CACHE


@evaluation_bp.route("/evaluation")
def evaluation_page():
    """Renders the comprehensive model evaluation page."""
    eval_data = get_evaluation_data()
    if eval_data is None:
        return render_template("evaluation.html", error="Evaluation artifacts not found in results/")

    return render_template("evaluation.html", eval_data=eval_data)
