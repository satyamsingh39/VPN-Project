"""
Flask application factory for the VPN Traffic Classifier web frontend.

Initializes the PredictionPipeline as an application-level singleton
and registers all route blueprints.
"""
import json
from pathlib import Path
from flask import Flask

from src.core.pipeline import PredictionPipeline
from src.config import PROJECT_ROOT


def create_app() -> Flask:
    """
    Application factory that creates and configures the Flask app.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    app.config["SECRET_KEY"] = "vpn-traffic-classifier-dev-key"
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64 MB upload limit

    # ── Load PredictionPipeline once at startup ──────────────────────
    try:
        pipeline = PredictionPipeline()
        app.config["PIPELINE"] = pipeline
        app.config["PIPELINE_READY"] = True
        app.config["PIPELINE_ERROR"] = None
    except Exception as exc:
        app.config["PIPELINE"] = None
        app.config["PIPELINE_READY"] = False
        app.config["PIPELINE_ERROR"] = str(exc)

    # ── Load evaluation metrics (if available) ───────────────────────
    metrics_path = PROJECT_ROOT / "results" / "hierarchical_metrics.json"
    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as f:
            app.config["EVAL_METRICS"] = json.load(f)
    else:
        app.config["EVAL_METRICS"] = None

    # ── Register Blueprints ──────────────────────────────────────────
    from src.web.routes.main import main_bp
    from src.web.routes.prediction import prediction_bp
    from src.web.routes.evaluation import evaluation_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(evaluation_bp)

    return app
