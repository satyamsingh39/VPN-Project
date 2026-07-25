# Hierarchical Encrypted Network Traffic Classification

An end-to-end machine learning and web application system designed to analyze and classify encrypted network traffic flows. The system identifies whether a traffic flow is routed through a Virtual Private Network (VPN) and maps it to its specific generating application category (such as browsing, streaming, chatting, file transfer, or VoIP) using statistical flow telemetry.

The project features a **hierarchical ML prediction pipeline** powered by scikit-learn & XGBoost, coupled with a **modern Flask-based web application** featuring interactive Plotly analytics, single-sample manual inference, batch CSV prediction, and full model evaluation reporting. (The legacy Streamlit dashboard is also preserved).

---

## 📐 Hierarchical Architecture

The classification pipeline employs a multi-tiered decision structure:

```text
       Input Network Flow
                │
                ▼
       ┌─────────────────┐
       │  VPN Detector   │ (Random Forest)
       └────────┬────────┘
                │
      ┌─────────┴─────────┐
      │                   │
      ▼ (VPN)             ▼ (Non-VPN)
┌──────────────┐    ┌──────────────┐
│VPN Classifier│    │  Non-VPN Clsf│ (XGBoost Multiclass)
└──────┬───────┘    └──────┬───────┘
       │                   │
       └─────────┬─────────┘
                 │
                 ▼
          Final Application
```

1. **Stage-1: VPN Detector**: Binary classifier (Random Forest) determining if a flow is `VPN` or `Non-VPN`.
2. **Stage-2: Application Classifiers**: Multiclass classifiers (XGBoost) routing VPN traffic to the `VPN Application Classifier` and standard traffic to the `Non-VPN Application Classifier`.

---

## 🔢 Telemetry Flow Features (23 inputs)

The pipeline utilizes 23 statistical flow metrics:
- **Flow Features**: `duration`, `total_fiat`, `total_biat`
- **Timing Features**: `min_fiat`, `min_biat`, `max_fiat`, `max_biat`, `mean_fiat`, `mean_biat`
- **Flow IAT (Inter-Arrival Time)**: `min_flowiat`, `max_flowiat`, `mean_flowiat`, `std_flowiat`
- **Active Time**: `min_active`, `mean_active`, `max_active`, `std_active`
- **Idle Time**: `min_idle`, `mean_idle`, `max_idle`, `std_idle`
- **Flow Statistics**: `flowPktsPerSecond`, `flowBytesPerSecond`

---

## 🏷️ Supported Application Classes

The pipeline outputs predictions for 14 final hierarchical categories:
- **Non-VPN Categories**: `BROWSING`, `CHAT`, `FT` (File Transfer), `MAIL`, `P2P`, `STREAMING`, `VOIP`
- **VPN Categories**: `VPN-BROWSING`, `VPN-CHAT`, `VPN-FT`, `VPN-MAIL`, `VPN-P2P`, `VPN-STREAMING`, `VPN-VOIP`

---

## 📊 Evaluation Results

Below are the metrics computed on the benchmark dataset (`59,706` flow records):

| Evaluation Layer | Metric | Score |
| :--- | :--- | :--- |
| **Stage-1 (VPN Detection)** | Accuracy | **93.40%** |
| | Precision | 92.68% |
| | Recall | 94.37% |
| | F1 Score | 93.51% |
| **End-to-End Hierarchical** | Accuracy | **85.55%** |
| | Weighted Precision | 87.67% |
| | Weighted Recall | 85.55% |
| | Weighted F1 Score | **85.63%** |
| | Macro F1 Score | **83.42%** |

> [!WARNING]
> **Data Leakage & Research Warning:** These metrics represent a full pipeline evaluation on the dataset. If some of these records were used during individual model training, these results may be optimistically biased. For unbiased research reporting, evaluate the pipeline on an independent, unseen test dataset.

---

## 💻 Web Interfaces & Tech Stack

### Technology Stack
- **Backend & Core ML**: Python 3.14+, Pandas, NumPy, Scikit-learn, XGBoost, Joblib
- **Web Framework**: Flask 3.1+ (App Factory pattern with Blueprints)
- **Frontend & Styling**: HTML5, Vanilla CSS3 (Dark Navy Glassmorphism Design System), Google Fonts (Inter + JetBrains Mono)
- **Data Visualizations**: Plotly.js (v2.35.2) & Chart.js (v4.4.4)
- **Legacy UI**: Streamlit (v1.30+)

### Flask Web Application Pages
- **`/` (Home)**: System overview, CSS-styled architecture flow diagram, estimator cards, and project highlights.
- **`/predict` (Inference & Analysis)**:
  - **Manual Prediction**: 23 grouped numerical inputs for instant single-sample flow classification with confidence breakdown.
  - **Batch Prediction**: Drag-and-drop CSV upload, batch inference, interactive Plotly charts (traffic type distribution, application breakdown, confidence score overlay, and telemetry scatter analytics), first 10 rows preview, and downloadable CSV output.
- **`/evaluation` (Model Evaluation & Analytics)**:
  - Overview metric cards for Stage-1 and End-to-End performance.
  - Interactive Plotly 14-class confusion matrix with cell annotations and hover details.
  - Per-class metrics (Precision, Recall, F1, Support) in grouped bar charts and responsive data tables.
  - Stage-level error breakdown (Routing vs. Application errors).
  - Top 10 misclassification pairs (confusion hotspots).
  - Prediction confidence density distribution (Correct vs. Incorrect).
  - Class performance insights and research summary discussion.
- **`/about` (System Architecture & Documentation)**:
  - Technical project overview, model specifications, dataset summary, 23-feature tag cloud, live performance metrics, and future roadmap.
- **`/api/health`**: JSON health check status endpoint for system monitoring.

---

## 📦 Folder Structure

```text
vpn_project/
├── flask_app.py                # Main Flask application entrypoint (python flask_app.py)
├── app.py                      # Streamlit application entrypoint (streamlit run app.py)
├── requirements.txt            # System dependencies (Flask, scikit-learn, xgboost, pandas, etc.)
├── run_pipeline.py             # CLI demonstration script
├── evaluate_pipeline.py        # E2E hierarchical evaluation script
├── datasets/                   # Flow CSV datasets (untracked)
├── results/                    # Confusion matrix, metrics JSON, evaluation outputs (untracked)
├── models/                     # Trained model binaries (untracked, via GitHub Releases)
│   ├── vpn_detector/           # vpn_random_forest_model.pkl, vpn_scaler.pkl, feature_columns.json
│   ├── vpn_application/        # best_vpn_application_model.pkl, vpn_application_scaler.pkl, ...
│   └── nonvpn_application/     # best_nonvpn_application_model.pkl, nonvpn_application_scaler.pkl, ...
└── src/
    ├── config.py               # Path configurations
    ├── core/
    │   └── pipeline.py         # Prediction pipeline orchestration (PredictionPipeline class)
    ├── models/                 # Model wrapper classes
    │   ├── vpn_detector.py
    │   ├── vpn_classifier.py
    │   └── nonvpn_classifier.py
    ├── ui/                     # Legacy Streamlit UI components
    │   ├── about.py
    │   ├── home.py
    │   ├── prediction.py
    │   └── sidebar.py
    ├── utils/                  # Helper utilities
    │   ├── loader.py           # JSON and Joblib loading functions
    │   └── preprocessing.py    # Feature validation, reordering, and scaling
    └── web/                    # Flask Web Frontend Package
        ├── __init__.py         # Flask App Factory & PredictionPipeline singleton
        ├── routes/             # Route Blueprints
        │   ├── main.py         # Home, About, Health routes
        │   ├── prediction.py   # Manual & Batch prediction routes, CSV download
        │   └── evaluation.py   # Model Evaluation analytics & metrics calculation
        ├── static/             # Static Assets
        │   ├── css/
        │   │   └── style.css   # Dark Navy Glassmorphism Design System
        │   └── js/
        │       └── app.js      # Client-side tab switching, drag-drop upload & Plotly chart renderers
        └── templates/          # Jinja2 HTML Templates
            ├── base.html       # Master layout with Google Fonts, Chart.js & Plotly CDN
            ├── home.html       # Landing page template
            ├── prediction.html # Inference & Analysis page template
            ├── evaluation.html # Model Evaluation page template
            ├── about.html      # About page template
            └── partials/       # Reusable UI partials (navbar, footer, results)
```

---

## 🚀 Installation & Setup

### 1. Download Model Binaries (GitHub Releases)
Model binaries (`.pkl`) are excluded from main git tracking due to file size limits. Download the files from **GitHub Releases** and place them in their respective subdirectories within `models/`:
- Place `vpn_random_forest_model.pkl` & `vpn_scaler.pkl` in `models/vpn_detector/`
- Place `best_vpn_application_model.pkl`, `vpn_application_scaler.pkl` & `vpn_application_label_encoder.pkl` in `models/vpn_application/`
- Place `best_nonvpn_application_model.pkl`, `nonvpn_application_scaler.pkl` & `nonvpn_application_label_encoder.pkl` in `models/nonvpn_application/`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Pipeline Evaluation
To evaluate the hierarchical pipeline on `datasets/dataset.csv`:
```bash
python evaluate_pipeline.py
```
This outputs performance metrics to console and writes `hierarchical_metrics.json`, `hierarchical_evaluation.csv`, and `hierarchical_confusion_matrix.png` into `results/`.

### 4. Launch Web Application

#### Option A: Run Flask Application (Recommended)
```bash
python flask_app.py
```
Access the application at `http://127.0.0.1:5000`.

#### Option B: Run Streamlit Application (Legacy)
```bash
streamlit run app.py
```
Access the Streamlit dashboard at `http://localhost:8501`.