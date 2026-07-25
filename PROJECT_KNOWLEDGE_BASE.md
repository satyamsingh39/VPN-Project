# Project Knowledge Base: Hierarchical Encrypted Network Traffic Classification

This document serves as a comprehensive, fact-based technical knowledge base for the Hierarchical Encrypted Network Traffic Classification project. It details the system architecture, datasets, features, preprocessing steps, machine learning models, prediction pipeline, evaluation results, software layout, Flask web application, Streamlit dashboard interfaces, and Plotly interactive analytics.

---

## 1. Project Overview
The objective of this project is to build an offline and interactive machine learning system that classifies encrypted network traffic flows. Specifically, it determines:
1. Whether the traffic flow is routed through a Virtual Private Network (VPN) or represents standard Non-VPN traffic (Stage 1).
2. The specific application category (e.g., Browsing, Streaming, VoIP, Chat, Mail, P2P, File Transfer) generating the traffic (Stage 2).

The final goal is to deliver a production-ready prediction pipeline wrapped in a **modern Flask web application** (as well as a legacy Streamlit UI) supporting single-sample (manual) prediction, batch (CSV) prediction, interactive Plotly visualization dashboards, and comprehensive model evaluation analytics.

---

## 2. Problem Statement
With the widespread adoption of encryption protocols (such as TLS, HTTPS, and VPN tunnels), traditional payload inspection methods (like Deep Packet Inspection - DPI) have become ineffective for traffic classification. Network administrators, security teams, and ISP providers need a way to analyze and categorize encrypted traffic for bandwidth shaping, QoS enforcement, and security auditing without compromising user privacy or decrypting payloads. 

This project solves this by using statistical flow telemetry characteristics (packet size averages, transmission rates, inter-arrival time metrics) rather than packet content to classify flows.

---

## 3. Overall System Architecture
The system uses a hierarchical classification architecture to route traffic flow records dynamically:

```text
               Input Traffic Flow Record
                           │
                           ▼
                 ┌───────────────────┐
                 │   VPN Detector    │ (Stage 1 - Random Forest)
                 └─────────┬─────────┘
                           │
                  Is VPN? ─┼───────────────┐
                           │ Yes           │ No
                           ▼               ▼
                 ┌───────────────────┐ ┌───────────────────┐
                 │  VPN Classifier   │ │Non-VPN Classifier │ (Stage 2 - XGBoost)
                 └─────────┬─────────┘ └───────────┬───────┘
                           │                       │
                           ▼                       ▼
                     Prediction (App)        Prediction (App)
                           │                       │
                           └───────────┬───────────┘
                                       ▼
                             Final Prediction Label
                        (e.g., VPN-BROWSING or BROWSING)
```

1. **Stage 1 (VPN vs. Non-VPN Detector)**: Classifies the incoming record as `VPN` or `Non-VPN` using a Random Forest model.
2. **Stage 2A (VPN Application Classifier)**: If predicted as `VPN`, routes the record to an XGBoost model to classify it into one of 7 VPN application categories.
3. **Stage 2B (Non-VPN Application Classifier)**: If predicted as `Non-VPN`, routes the record to an XGBoost model to classify it into one of 7 standard application categories.

---

## 4. Dataset
All dataset properties are derived from `datasets/dataset.csv`:
- **Source**: ISCX VPN-NonVPN benchmark flow dataset.
- **Total Samples**: 59,706 records (verified via `evaluate_pipeline.py`).
- **Ground-Truth Column**: `traffic_type` (categorical string).
- **Target Distribution**:
  - `BROWSING`: 4,591 samples
  - `CHAT`: 2,560 samples
  - `FT`: 4,964 samples
  - `MAIL`: 570 samples
  - `P2P`: 804 samples
  - `STREAMING`: 1,940 samples
  - `VOIP`: 13,635 samples
  - `VPN-BROWSING`: 4,008 samples
  - `VPN-CHAT`: 2,709 samples
  - `VPN-FT`: 2,360 samples
  - `VPN-MAIL`: 4,547 samples
  - `VPN-P2P`: 2,420 samples
  - `VPN-STREAMING`: 5,917 samples
  - `VPN-VOIP`: 8,681 samples

---

## 5. Input Features & Preprocessing Schema
The model uses 23 statistical flow features:
- **Flow Features**: `duration`, `total_fiat`, `total_biat`
- **Timing Features**: `min_fiat`, `min_biat`, `max_fiat`, `max_biat`, `mean_fiat`, `mean_biat`
- **Flow IAT (Inter-Arrival Time)**: `min_flowiat`, `max_flowiat`, `mean_flowiat`, `std_flowiat`
- **Active Time**: `min_active`, `mean_active`, `max_active`, `std_active`
- **Idle Time**: `min_idle`, `mean_idle`, `max_idle`, `std_idle`
- **Flow Statistics**: `flowPktsPerSecond`, `flowBytesPerSecond`

### Preprocessing Logic (`src/utils/preprocessing.py`)
1. **Column Filtering & Validation**: Checks for missing required columns against `feature_columns.json`.
2. **Reordering**: Reorders columns to strictly match training order.
3. **Standard Scaling**: Applies pre-trained `StandardScaler` transformations.

---

## 6. Machine Learning Models Summary

| Model Role | File Path | Algorithm | Scaler File | Label Encoder File |
|---|---|---|---|---|
| **VPN Detector** | `models/vpn_detector/vpn_random_forest_model.pkl` | Random Forest Classifier | `vpn_scaler.pkl` | N/A (Binary 0/1) |
| **VPN Classifier** | `models/vpn_application/best_vpn_application_model.pkl` | XGBoost Multiclass | `vpn_application_scaler.pkl` | `vpn_application_label_encoder.pkl` |
| **Non-VPN Classifier** | `models/nonvpn_application/best_nonvpn_application_model.pkl` | XGBoost Multiclass | `nonvpn_application_scaler.pkl` | `nonvpn_application_label_encoder.pkl` |

---

## 7. Prediction Pipeline (`src/core/pipeline.py`)
The `PredictionPipeline` class wraps all three model stages into a single framework-agnostic orchestrator:
- **`__init__()`**: Loads all 3 models, scalers, and encoders into memory once during application startup.
- **`predict(df)`**:
  - Accepts a pandas DataFrame.
  - Passes features to `VPNDetector`.
  - Splits samples into VPN and Non-VPN indices.
  - Passes VPN samples to `VPNClassifier` and Non-VPN samples to `NonVPNClassifier`.
  - Reconstructs predictions into unified output columns (`Traffic Type`, `Traffic Confidence`, `Application`, `Application Confidence`) while preserving all original input columns and row order.
- **`predict_csv(csv_path)`**: Loads a CSV file, runs `predict()`, and returns result DataFrames, metrics dictionaries, and summary frequency statistics.

---

## 8. Web Applications & Frontend Architecture

### Flask Web Application (Primary Production Interface)
Entrypoint: `flask_app.py` | Package: `src/web/`
- **Architecture**: Flask App Factory (`create_app()`) with Blueprint routes, app-level singleton for `PredictionPipeline`, and Jinja2 template inheritance.
- **Styling**: Vanilla CSS (`src/web/static/css/style.css`) implementing a Dark Navy Glassmorphism design system, responsive grid layouts, Inter and JetBrains Mono typography, and CSS micro-animations.
- **Visualization Libraries**: Plotly.js (v2.35.2 CDN) for interactive scatter plots, confusion matrix heatmaps, grouped bar charts, and histograms; Chart.js (v4.4.4 CDN) for donut/bar summaries.

#### Routes & Pages
1. **GET `/` (Home)**:
   - Hero banner, interactive pipeline architecture flow diagram, 3 ML model specification cards, and project highlights.
2. **GET & POST `/predict` (Inference & Analysis)**:
   - **Manual Tab**: Single-sample manual prediction with 23 grouped numerical input fields. Returns traffic type, application label, confidence scores, and model execution time.
   - **Batch Tab**: Drag-and-drop CSV upload, batch inference execution, summary metric cards, interactive Plotly charts (traffic type distribution, application breakdown, confidence overlay histogram, and flow duration vs bytes/sec scatter analytics), first 10 rows preview, and downloadable predictions CSV (`/predict/download`).
3. **GET `/evaluation` (Model Evaluation & Analytics)**:
   - Stage 1 and End-to-End metric cards (Accuracy, Precision, Recall, F1).
   - Interactive Plotly 14-class confusion matrix with cell counts and hover details.
   - Per-class metrics table and Plotly grouped bar chart comparing Precision, Recall, and F1.
   - Stage-level error distribution (Routing vs. Application errors).
   - Top 10 misclassification pairs (confusion hotspots).
   - Prediction confidence distribution overlay (Correct vs. Incorrect).
   - Class performance insights and academic research summary discussion.
4. **GET `/about` (System Architecture & Documentation)**:
   - Technical project overview, model specifications, dataset details, 23-feature tag cloud, live performance metrics (from `results/hierarchical_metrics.json`), and future roadmap.
5. **GET `/api/health`**:
   - JSON health status endpoint returning pipeline readiness and model load state.

### Streamlit Application (Legacy Interface)
Entrypoint: `app.py` | Modules: `src/ui/`
- Rendered using Streamlit components (`st.tabs`, `st.number_input`, `st.file_uploader`, `st.dataframe`, `st.bar_chart`).
- Preserved in working state for comparative evaluation.

---

## 9. Software Directory Structure

```text
vpn_project/
├── flask_app.py                # Main Flask application entrypoint (python flask_app.py)
├── app.py                      # Streamlit application entrypoint (streamlit run app.py)
├── requirements.txt            # Package dependencies (Flask, scikit-learn, xgboost, pandas, etc.)
├── run_pipeline.py             # CLI demonstration script
├── evaluate_pipeline.py        # Pipeline evaluation script
├── check_features.py           # Feature verification utility
├── test_models.py              # Backend unit test script
├── PROJECT_KNOWLEDGE_BASE.md   # Comprehensive project technical knowledge base
├── README.md                   # Project overview & documentation
├── datasets/                   # Flow CSV datasets (untracked)
│   ├── dataset.csv             # Full combined benchmark dataset (~59,706 rows)
│   ├── vpn_only_dataset.csv    # VPN-only flow subset
│   └── nonvpn_only_dataset.csv # Non-VPN flow subset
├── results/                    # Generated evaluation artifacts (untracked)
│   ├── hierarchical_evaluation.csv
│   ├── hierarchical_metrics.json
│   ├── hierarchical_confusion_matrix.png
│   └── predictions.csv
├── models/                     # Trained model binaries (untracked, via GitHub Releases)
│   ├── vpn_detector/           # vpn_random_forest_model.pkl, vpn_scaler.pkl, feature_columns.json
│   ├── vpn_application/        # best_vpn_application_model.pkl, vpn_application_scaler.pkl, ...
│   └── nonvpn_application/     # best_nonvpn_application_model.pkl, nonvpn_application_scaler.pkl, ...
└── src/
    ├── config.py               # Centralized path configuration constants
    ├── core/
    │   └── pipeline.py         # PredictionPipeline orchestrator class
    ├── models/                 # Classifier wrapper classes
    │   ├── vpn_detector.py     # VPNDetector class wrapper
    │   ├── vpn_classifier.py   # VPNClassifier class wrapper
    │   └── nonvpn_classifier.py # NonVPNClassifier class wrapper
    ├── ui/                     # Legacy Streamlit UI components
    │   ├── sidebar.py          # Streamlit navigation sidebar
    │   ├── home.py             # Streamlit landing page
    │   ├── prediction.py       # Streamlit prediction page
    │   └── about.py            # Streamlit about page
    ├── utils/                  # Utility helpers
    │   ├── loader.py           # joblib & json loader functions
    │   └── preprocessing.py    # Feature validation, reordering, and scaling
    └── web/                    # Flask Web Application Package
        ├── __init__.py         # App factory & PredictionPipeline singleton
        ├── routes/             # Blueprint Route Handlers
        │   ├── main.py         # Home, About, Health routes
        │   ├── prediction.py   # Manual & Batch prediction routes, CSV download
        │   └── evaluation.py   # Model Evaluation analytics & metrics computation
        ├── static/             # Static Web Assets
        │   ├── css/
        │   │   └── style.css   # Dark Navy Glassmorphism Design System
        │   └── js/
        │       └── app.js      # Client-side tabs, drag-drop upload & Plotly chart renderers
        └── templates/          # Jinja2 HTML Templates
            ├── base.html       # Master layout with Google Fonts, Chart.js & Plotly CDN
            ├── home.html       # Home page template
            ├── prediction.html # Inference & Analysis page template
            ├── evaluation.html # Model Evaluation page template
            ├── about.html      # About page template
            └── partials/       # UI Partials (navbar, footer, results)
```

---

## 10. Experimental Evaluation & Benchmark Results

Derived from `results/hierarchical_metrics.json` and `evaluate_pipeline.py` on the full `dataset.csv` (59,706 samples):

### 1. Stage-1 VPN Detection (Binary)
- **Accuracy**: **93.40%**
- **Precision**: **92.68%**
- **Recall**: **94.37%**
- **F1 Score**: **93.51%**

### 2. End-to-End Hierarchical Classification (14 Classes)
- **Total Samples**: 59,706
- **Correct Predictions**: 51,077
- **Incorrect Predictions**: 8,629
- **Accuracy**: **85.55%**
- **Weighted Precision**: **87.67%**
- **Weighted Recall**: **85.55%**
- **Weighted F1 Score**: **85.63%**
- **Macro Precision**: **88.55%**
- **Macro Recall**: **80.87%**
- **Macro F1 Score**: **83.42%**

### 3. Stage-Level Error Analysis
- **Stage-1 Routing Errors**: 3,939 samples (**6.60%**) misclassified at the binary VPN / Non-VPN layer.
- **Stage-2 Application Errors**: 4,690 samples (**7.86%**) correctly routed but assigned to the wrong application label.

### 4. Confidence Score Analysis
- **Correct Predictions**: Average application confidence = **0.9664** (~96.6%)
- **Incorrect Predictions**: Average application confidence = **0.7675** (~76.8%)

### 5. Class Insights
- **Top 3 Strongest Classes (F1)**: `BROWSING` (97.02%), `VPN-VOIP` (96.47%), `VPN-FT` (96.11%).
- **Top 3 Weakest Classes (F1)**: `P2P` (54.20%), `VPN-STREAMING` (68.61%), `VPN-P2P` (75.05%).
- **Top Misclassification Pair**: `VPN-STREAMING → STREAMING` (1,650 misclassified flows).

---

## 11. Limitations & Discussion
- **Data Leakage Risk**: Evaluation was performed on `dataset.csv` without an explicit train/test partition file. If samples were included during model training, metrics reflect train/validation performance rather than unseen test generalization.
- **Cascading Error Propagation**: Mistakes made by the Stage-1 VPN Detector route traffic to the incorrect secondary branch, causing irreversible application classification errors.
- **Offline Batch Dependency**: System currently processes static CSV statistical flow summaries rather than raw live network interface streams.

---

## 12. Future Roadmap
- **SHAP Explainability**: Incorporate SHAP values into the Flask prediction UI to highlight which telemetry features contributed most to each classification.
- **Live Interface Capture**: Stream PCAP data from active interfaces using Scapy, compute 23 statistical flow metrics in real time, and feed them into `PredictionPipeline`.
- **FastAPI / REST API Microservices**: Package `PredictionPipeline` into a lightweight async REST API for high-throughput network monitoring tools.
- **Docker Containerization**: Containerize Flask web service and ML backend into single multi-stage Docker builds.

---

## 13. Reproducibility & Commands

### Setup Environment
```bash
pip install -r requirements.txt
```

### Run Model Evaluation Script
```bash
python evaluate_pipeline.py
```

### Launch Flask Web Application (Recommended)
```bash
python flask_app.py
```
Open `http://127.0.0.1:5000` in browser.

### Launch Legacy Streamlit Dashboard
```bash
streamlit run app.py
```
Open `http://localhost:8501` in browser.

---

## 14. Summary Table for Academic Reports

| Layer / Metric | Samples | Accuracy | Weighted F1 | Macro F1 | Correct | Incorrect |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1 (VPN Detection)** | 59,706 | **93.40%** | **93.51%** (Binary F1) | N/A | N/A | N/A |
| **Hierarchical (End-to-End)** | 59,706 | **85.55%** | **85.63%** | **83.42%** | **51,077** | **8,629** |
