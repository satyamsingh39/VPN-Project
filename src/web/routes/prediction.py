"""
Prediction routes blueprint — Manual single-sample and batch CSV prediction.
"""
import time
from pathlib import Path

import pandas as pd
from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    send_file,
    flash,
    redirect,
    url_for,
)

from src.config import PROJECT_ROOT

prediction_bp = Blueprint("prediction", __name__)

# ── Feature group definitions (matches Streamlit layout) ─────────────
FEATURE_GROUPS = {
    "Flow Features": ["duration", "total_fiat", "total_biat"],
    "Timing Features": [
        "min_fiat", "min_biat", "max_fiat",
        "max_biat", "mean_fiat", "mean_biat",
    ],
    "Flow IAT": ["min_flowiat", "max_flowiat", "mean_flowiat", "std_flowiat"],
    "Active Time": ["min_active", "mean_active", "max_active", "std_active"],
    "Idle Time": ["min_idle", "mean_idle", "max_idle", "std_idle"],
    "Flow Statistics": ["flowPktsPerSecond", "flowBytesPerSecond"],
}


def _get_pipeline():
    """Retrieve the PredictionPipeline from app config."""
    return current_app.config.get("PIPELINE")


def _pipeline_ready():
    """Check if the pipeline is loaded and operational."""
    return current_app.config.get("PIPELINE_READY", False)


@prediction_bp.route("/predict")
def predict_page():
    """Render the empty prediction form page."""
    if not _pipeline_ready():
        error = current_app.config.get("PIPELINE_ERROR", "Pipeline failed to load.")
        return render_template("prediction.html", pipeline_error=error)

    pipeline = _get_pipeline()
    feature_columns = pipeline.detector.feature_columns
    return render_template(
        "prediction.html",
        feature_groups=FEATURE_GROUPS,
        feature_columns=feature_columns,
    )


@prediction_bp.route("/predict/manual", methods=["POST"])
def manual_predict():
    """Handle a single-sample manual prediction from form data."""
    if not _pipeline_ready():
        flash("Pipeline is not ready. Cannot perform prediction.", "error")
        return redirect(url_for("prediction.predict_page"))

    pipeline = _get_pipeline()
    feature_columns = pipeline.detector.feature_columns

    try:
        # Build single-row dict from form inputs
        inputs = {}
        for col in feature_columns:
            raw = request.form.get(col, "0")
            inputs[col] = float(raw)

        input_df = pd.DataFrame([inputs])

        start = time.perf_counter()
        result_df = pipeline.predict(input_df)
        elapsed = time.perf_counter() - start

        result = {
            "traffic_type": str(result_df["Traffic Type"].values[0]),
            "traffic_confidence": float(result_df["Traffic Confidence"].values[0]),
            "application": str(result_df["Application"].values[0]),
            "app_confidence": float(result_df["Application Confidence"].values[0]),
            "prediction_time": round(elapsed, 4),
            "model_level2": (
                "VPN Classifier (XGBoost)"
                if result_df["Traffic Type"].values[0] == "VPN"
                else "Non-VPN Classifier (XGBoost)"
            ),
            "feature_count": len(feature_columns),
        }

        return render_template(
            "prediction.html",
            feature_groups=FEATURE_GROUPS,
            feature_columns=feature_columns,
            manual_result=result,
            form_values=inputs,
        )

    except Exception as exc:
        flash(f"Prediction failed: {exc}", "error")
        return redirect(url_for("prediction.predict_page"))


@prediction_bp.route("/predict/batch", methods=["POST"])
def batch_predict():
    """Handle a batch CSV file prediction."""
    if not _pipeline_ready():
        flash("Pipeline is not ready. Cannot perform prediction.", "error")
        return redirect(url_for("prediction.predict_page"))

    pipeline = _get_pipeline()
    feature_columns = pipeline.detector.feature_columns

    file = request.files.get("csv_file")
    if file is None or file.filename == "":
        flash("No CSV file selected. Please upload a file.", "error")
        return redirect(url_for("prediction.predict_page"))

    try:
        df = pd.read_csv(file)
    except Exception as exc:
        flash(f"Failed to read CSV file: {exc}", "error")
        return redirect(url_for("prediction.predict_page"))

    # Validate feature columns
    missing = [c for c in feature_columns if c not in df.columns]
    if missing:
        flash(f"CSV is missing required columns: {missing}", "error")
        return redirect(url_for("prediction.predict_page"))

    try:
        results_df = pipeline.predict(df)

        # Save predictions to results/
        results_dir = PROJECT_ROOT / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        output_path = results_dir / "predictions.csv"
        results_df.to_csv(output_path, index=False)

        # Build traffic stats
        traffic_stats = pipeline.traffic_stats.to_dict("records")
        app_stats = pipeline.application_stats.to_dict("records")

        # Breakdown by VPN vs Non-VPN Application distributions
        vpn_mask = results_df["Traffic Type"] == "VPN"
        nonvpn_mask = results_df["Traffic Type"] == "Non-VPN"

        vpn_app_counts = results_df[vpn_mask]["Application"].value_counts().to_dict()
        nonvpn_app_counts = results_df[nonvpn_mask]["Application"].value_counts().to_dict()

        vpn_app_stats = [{"Application": app, "Count": int(cnt)} for app, cnt in vpn_app_counts.items()]
        nonvpn_app_stats = [{"Application": app, "Count": int(cnt)} for app, cnt in nonvpn_app_counts.items()]

        # Extract confidence scores for distribution analytical graph
        traffic_confidences = results_df["Traffic Confidence"].round(4).tolist()
        app_confidences = results_df["Application Confidence"].round(4).tolist()

        # Sample up to 500 rows for scatter analysis to keep rendering fast
        scatter_sample = results_df.head(500)
        scatter_data = []
        for _, row in scatter_sample.iterrows():
            scatter_data.append({
                "duration": float(row.get("duration", 0)),
                "flowBytesPerSecond": float(row.get("flowBytesPerSecond", 0)),
                "flowPktsPerSecond": float(row.get("flowPktsPerSecond", 0)),
                "mean_flowiat": float(row.get("mean_flowiat", 0)),
                "traffic_type": str(row.get("Traffic Type", "")),
                "application": str(row.get("Application", "")),
                "app_confidence": float(row.get("Application Confidence", 0))
            })

        batch_result = {
            "total": len(results_df),
            "metrics": pipeline.metrics,
            "traffic_stats": traffic_stats,
            "app_stats": app_stats,
            "vpn_app_stats": vpn_app_stats,
            "nonvpn_app_stats": nonvpn_app_stats,
            "traffic_confidences": traffic_confidences,
            "app_confidences": app_confidences,
            "scatter_data": scatter_data,
            "preview_html": results_df.head(10).to_html(
                classes="results-table", index=False, border=0
            ),
            "filename": file.filename,
        }

        return render_template(
            "prediction.html",
            feature_groups=FEATURE_GROUPS,
            feature_columns=feature_columns,
            batch_result=batch_result,
        )

    except Exception as exc:
        flash(f"Batch prediction failed: {exc}", "error")
        return redirect(url_for("prediction.predict_page"))


@prediction_bp.route("/predict/download")
def download_predictions():
    """Serve the latest predictions.csv for download."""
    output_path = PROJECT_ROOT / "results" / "predictions.csv"
    if not output_path.exists():
        flash("No prediction results available for download.", "error")
        return redirect(url_for("prediction.predict_page"))

    return send_file(
        str(output_path),
        mimetype="text/csv",
        as_attachment=True,
        download_name="predictions.csv",
    )
