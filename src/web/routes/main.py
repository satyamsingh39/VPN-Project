"""
Main routes blueprint — Home, About, and API health check.
"""
from flask import Blueprint, render_template, jsonify, current_app

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Render the landing / home page."""
    return render_template("home.html")


@main_bp.route("/about")
def about():
    """Render the about page with evaluation metrics if available."""
    eval_metrics = current_app.config.get("EVAL_METRICS")
    return render_template("about.html", eval_metrics=eval_metrics)


@main_bp.route("/api/health")
def health():
    """JSON health-check endpoint for monitoring."""
    pipeline_ready = current_app.config.get("PIPELINE_READY", False)
    error = current_app.config.get("PIPELINE_ERROR")

    status = "healthy" if pipeline_ready else "unhealthy"
    response = {
        "status": status,
        "pipeline_ready": pipeline_ready,
        "models_loaded": pipeline_ready,
    }
    if error:
        response["error"] = error

    code = 200 if pipeline_ready else 503
    return jsonify(response), code
