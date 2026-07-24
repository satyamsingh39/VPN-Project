# Project Knowledge Base: Hierarchical Encrypted Network Traffic Classification

This document serves as a comprehensive, fact-based technical knowledge base for the Hierarchical Encrypted Network Traffic Classification project. It details the system architecture, datasets, features, preprocessing steps, machine learning models, prediction pipeline, evaluation results, software layout, and Streamlit application interfaces.

---

## 1. Project Overview
The objective of this project is to build an offline and interactive machine learning system that classifies encrypted network traffic flows. Specifically, it determines:
1. Whether the traffic flow is routed through a Virtual Private Network (VPN) or represents standard Non-VPN traffic (Stage 1).
2. The specific application category (e.g., Browsing, Streaming, VoIP, Chat, Mail, P2P, File Transfer) generating the traffic (Stage 2).

The final goal is to deliver a production-ready prediction pipeline wrapped in a Streamlit UI for single-sample (manual) and batch (CSV) predictions.

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
- **Source**: Unknown (unspecified in the repository).
- **Total Samples**: 59,706 records (verified via `evaluate_pipeline.py`).
- **Ground-Truth Column**: `traffic_type` (categorical string).
- **Original Labels**:
  - `BROWSING` (10,000)
  - `VPN-BROWSING` (10,000)
  - `VOIP` (6,485)
  - `VPN-VOIP` (5,576)
  - `VPN-FT` (4,704)
  - `P2P` (4,000)
  - `FT` (3,975)
  - `VPN-P2P` (3,415)
  - `VPN-CHAT` (2,839)
  - `CHAT` (2,505)
  - `VPN-MAIL` (2,444)
  - `MAIL` (1,364)
  - `STREAMING` (1,284)
  - `VPN-STREAMING` (1,115)
- **Derived Stage-1 Labels**: `VPN` (if starts with `VPN-`), else `Non-VPN`.
- **Stage-2 Application Classes**: `BROWSING`, `CHAT`, `FT`, `MAIL`, `P2P`, `STREAMING`, `VOIP`.
- **Sub-Datasets**: 
  - `datasets/vpn_only_dataset.csv` (30,095 records).
  - `datasets/nonvpn_only_dataset.csv` (29,615 records).
- **Train/Val/Test Splits & Balancing**: UNKNOWN. The repository contains pre-trained models; no training logs, splits, or sampling scripts exist.

---

## 5. Input Features
The system uses exactly **23 features** defined in `feature_columns.json`:

1. `duration`: Length of the flow session.
2. `total_fiat`: Total forward inter-arrival time.
3. `total_biat`: Total backward inter-arrival time.
4. `min_fiat`: Minimum forward inter-arrival time.
5. `min_biat`: Minimum backward inter-arrival time.
6. `max_fiat`: Maximum forward inter-arrival time.
7. `max_biat`: Maximum backward inter-arrival time.
8. `mean_fiat`: Average forward inter-arrival time.
9. `mean_biat`: Average backward inter-arrival time.
10. `flowPktsPerSecond`: Packet transmission rate per second.
11. `flowBytesPerSecond`: Byte transmission rate per second.
12. `min_flowiat`: Minimum flow inter-arrival time.
13. `max_flowiat`: Maximum flow inter-arrival time.
14. `mean_flowiat`: Average flow inter-arrival time.
15. `std_flowiat`: Standard deviation of flow inter-arrival times.
16. `min_active`: Minimum active time before going idle.
17. `mean_active`: Average active time.
18. `max_active`: Maximum active time.
19. `std_active`: Standard deviation of active times.
20. `min_idle`: Minimum idle time.
21. `mean_idle`: Average idle time.
22. `max_idle`: Maximum idle time.
23. `std_idle`: Standard deviation of idle times.

---

## 6. Data Preprocessing
### Preprocessing during Inference
Implemented in `src/utils/preprocessing.py`:
1. **Type Checking**: Inputs must be a `pandas.DataFrame`, a `dict`, or a `list` of `dict` records.
2. **Feature Validation**: Validates that all 23 expected columns exist. If any are missing, raises a `ValueError`. Extra columns are ignored.
3. **Reordering**: Sorts columns to match the 23 features exactly in the training layout order.
4. **Standardization Scaling**: Applies `scaler.transform()` using the corresponding pre-loaded `StandardScaler`.

### Preprocessing during Training
UNKNOWN. Training scripts are not present in the workspace.

---

## 7. Stage 1 — VPN vs. Non-VPN Detector
- **Algorithm Selected**: `Random Forest Classifier` (loaded from `vpn_random_forest_model.pkl`).
- **Scaler**: `vpn_scaler.pkl` (`StandardScaler`).
- **Feature Schema**: `models/vpn_detector/feature_columns.json`.
- **Stage-1 Metrics**: Accuracy: **93.40%**, Precision: **92.68%**, Recall: **94.37%**, F1 Score: **93.51%** (zero_division=0).
- **Hyperparameters, Cross-Validation & Tuning details**: UNKNOWN.

---

## 8. Stage 2A — VPN Application Classifier
- **Algorithm Selected**: `XGBoost Classifier` (loaded from `best_vpn_application_model.pkl`).
- **Scaler**: `vpn_application_scaler.pkl` (`StandardScaler`).
- **Label Encoder**: `vpn_application_label_encoder.pkl` (decodes numbers to `BROWSING`, `CHAT`, `FT`, `MAIL`, `P2P`, `STREAMING`, `VOIP`).
- **Feature Schema**: `models/vpn_application/feature_columns.json`.
- **Hyperparameters, Cross-Validation & Tuning details**: UNKNOWN.

---

## 9. Stage 2B — Non-VPN Application Classifier
- **Algorithm Selected**: `XGBoost Classifier` (loaded from `best_nonvpn_application_model.pkl`).
- **Scaler**: `nonvpn_application_scaler.pkl` (`StandardScaler`).
- **Label Encoder**: `nonvpn_application_label_encoder.pkl` (decodes numbers to `BROWSING`, `CHAT`, `FT`, `MAIL`, `P2P`, `STREAMING`, `VOIP`).
- **Feature Schema**: `models/nonvpn_application/feature_columns.json`.
- **Hyperparameters, Cross-Validation & Tuning details**: UNKNOWN.

---

## 10. Model Comparison
No model comparison logs exist in the repository. We can only report metrics calculated on the final models:

| Model / Stage | Estimator Type | Features Count | Task |
| :--- | :--- | :--- | :--- |
| **Stage 1 (VPN Detector)** | Random Forest | 23 | Binary classification |
| **Stage 2A (VPN Application)** | XGBoost | 23 | Multiclass classification |
| **Stage 2B (Non-VPN Application)** | XGBoost | 23 | Multiclass classification |

---

## 11. Hierarchical Prediction Pipeline
Implemented in [pipeline.py](file:///d:/IISc/vpn_project/src/core/pipeline.py):
1. **Instantiation**: Loads models, scalers, and label encoders once during initialization.
2. **Column Validation**: Verifies that the input contains the 23 required features.
3. **Preprocessing**: Validates, reorders, and applies `StandardScaler`.
4. **VPN Detection**: Predicts binary classes (0 for Non-VPN, 1 for VPN) and prediction probabilities using `detector.predict()`.
5. **Vectorized Routing**:
   - Isolates indices classified as `1` and passes their inputs to `vpn_classifier.predict()`.
   - Isolates indices classified as `0` and passes their inputs to `nonvpn_classifier.predict()`.
6. **Reconstruction**: Combines predictions and confidence values back into the original order. Returns a DataFrame preserving all original columns with the appended prediction columns: `Traffic Type`, `Traffic Confidence`, `Application`, and `Application Confidence`.

---

## 12. End-to-End Hierarchical Evaluation
Calculated by running `evaluate_pipeline.py` on the full `dataset.csv`:
- **Total Samples**: 59,706
- **Correct Predictions**: 51,077
- **Incorrect Predictions**: 8,629
- **Overall Accuracy**: **85.55%**
- **Weighted Precision**: **87.67%**
- **Weighted Recall**: **85.55%**
- **Weighted F1 Score**: **85.63%**
- **Macro Precision**: 88.55%
- **Macro Recall**: 80.87%
- **Macro F1 Score**: **83.42%**

### Hierarchical Error Propagation
Because Stage 2 application classification depends on the Stage-1 routing prediction, any error in the VPN Detector propagates downward. For example, if a `VPN-BROWSING` sample is incorrectly classified as `Non-VPN` at Stage 1, it is sent to the `Non-VPN Classifier`, where it can never predict `VPN-BROWSING`, resulting in a cascaded classification error.

---

## 13. Software Architecture
```text
vpn_project/
├── app.py                      # Streamlit application entry point
├── requirements.txt            # Package dependencies
├── run_pipeline.py             # CLI demonstration script
├── evaluate_pipeline.py        # Pipeline evaluation script
└── src/
    ├── config.py               # Centralized path variables
    ├── core/
    │   └── pipeline.py         # Main PredictionPipeline class orchestrator
    ├── models/
    │   ├── vpn_detector.py     # Stage-1 Random Forest wrapper
    │   ├── vpn_classifier.py   # Stage-2A XGBoost wrapper
    │   └── nonvpn_classifier.py # Stage-2B XGBoost wrapper
    ├── ui/
    │   ├── sidebar.py          # Dashboard navigation sidebar layout
    │   ├── home.py             # Dashboard landing page and flowcharts
    │   ├── prediction.py       # Single-sample & batch classification interfaces
    │   └── about.py            # Overview & Future roadmap details
    └── utils/
        ├── loader.py           # joblib & json loader helpers
        └── preprocessing.py    # Feature validation, reordering, and scaling
```

---

## 14. Streamlit Application
- **Pages**:
  - `Home`: Displays the architecture flowchart and information cards.
  - `Prediction`: Contains prediction tabs:
    - *Manual Prediction Tab*: Renders inputs for the 23 features dynamically. Displays results in metrics cards.
    - *Batch Prediction Tab*: Allows CSV uploads, previews the first 5 rows, runs batch inference, and displays performance timing summaries, traffic/application distribution charts (`st.bar_chart`), and a download button.
  - `About`: Explains dataset details, features, and future enhancements.

---

## 15. Saved Artifacts

| Artifact Name | Path | Purpose |
| :--- | :--- | :--- |
| **VPN Detector Model** | `models/vpn_detector/vpn_random_forest_model.pkl` | Binary Random Forest classifier binary |
| **VPN Scaler** | `models/vpn_detector/vpn_scaler.pkl` | StandardScaler for Stage 1 |
| **Detector Column Config** | `models/vpn_detector/feature_columns.json` | Feature schema for Stage 1 |
| **VPN App Model** | `models/vpn_application/best_vpn_application_model.pkl` | Multiclass XGBoost classifier binary |
| **VPN App Scaler** | `models/vpn_application/vpn_application_scaler.pkl` | StandardScaler for Stage 2A |
| **VPN App Label Encoder** | `models/vpn_application/vpn_application_label_encoder.pkl` | Decodes predicted indices to strings |
| **VPN App Column Config** | `models/vpn_application/feature_columns.json` | Feature schema for Stage 2A |
| **Non-VPN App Model** | `models/nonvpn_application/best_nonvpn_application_model.pkl` | Multiclass XGBoost classifier binary |
| **Non-VPN App Scaler** | `models/nonvpn_application/nonvpn_application_scaler.pkl` | StandardScaler for Stage 2B |
| **Non-VPN Label Encoder** | `models/nonvpn_application/nonvpn_application_label_encoder.pkl` | Decodes predicted indices to strings |
| **Non-VPN Column Config** | `models/nonvpn_application/feature_columns.json` | Feature schema for Stage 2B |
| **E2E Evaluation CSV** | `results/hierarchical_evaluation.csv` | Full row-level evaluation predictions |
| **Metrics Summary JSON** | `results/hierarchical_metrics.json` | Overall evaluation statistics |
| **Confusion Matrix Heatmap** | `results/hierarchical_confusion_matrix.png` | Matplotlib heatmap plot image |
| **Predictions CSV** | `results/predictions.csv` | Batch predictions export |

---

## 16. Experimental Results
Derived from `results/hierarchical_metrics.json` and `evaluate_pipeline.py`:

- **Stage-1 (VPN Detection)**:
  - Accuracy: **93.40%**
  - Precision: **92.68%**
  - Recall: **94.37%**
  - F1 Score: **93.51%**
- **End-to-End Hierarchical Classification**:
  - Accuracy: **85.55%**
  - Weighted Precision: **87.67%**
  - Weighted Recall: **85.55%**
  - Weighted F1 Score: **85.63%**
  - Macro Precision: **88.55%**
  - Macro Recall: **80.87%**
  - Macro F1 Score: **83.42%**

---

## 17. Figures Available for the Report

| Figure file | Path | What it shows | Report Section | Importance |
| :--- | :--- | :--- | :--- | :--- |
| `hierarchical_confusion_matrix.png` | `results/hierarchical_confusion_matrix.png` | Heatmap confusion matrix of the 14 traffic classes | Experimental Results | **Essential** |

---

## 18. Tables That Can Be Generated

1. **Dataset Class Distribution Table**: Generated using `traffic_type.value_counts()` from `datasets/dataset.csv`.
2. **Performance Metrics Table**: Extracted from `results/hierarchical_metrics.json`.
3. **Per-class Precision/Recall/F1 Table**: Extracted from `classification_report` output in `evaluate_pipeline.py`.

---

## 19. Research Contributions
- **Implementation Contributions**: Implemented a vectorized routing pipeline that minimizes multiclass model space search and scales predictions across large datasets.
- **System Design Contributions**: Structured a unified workflow combining path routing (`src/config.py`), automatic feature validation, and a dashboard using Streamlit.

---

## 20. Limitations
- **Data Leakage Risk**: Evaluation was performed on the same dataset file (`dataset.csv`) that likely contains training samples.
- **Cascading Error Propagation**: Inaccuracies in the Stage 1 VPN Detector route traffic to the incorrect application classifier, creating irreversible classification errors.
- **Offline Batch Dependency**: The system currently runs on static CSV traffic flow statistics instead of live packet captures.

---

## 21. Future Work
- **REST API & Docker Integration**: Deploying the hierarchical model using FastAPI and containerizing it with Docker for production routing.
- **Live Interface Capture**: Using Scapy or similar libraries to capture live traffic from network interfaces and extract the 23 features in real-time.
- **Explainable AI (SHAP)**: Integrating Shapley values to interpret features influencing classification decisions.

---

## 22. Reproducibility
### 1. Environment Setup
```bash
pip install -r requirements.txt
```
### 2. Run Evaluation
```bash
python evaluate_pipeline.py
```
### 3. Run Streamlit Dashboard
```bash
streamlit run app.py
```

---

## 23. Report-Ready Key Numbers

| Layer | Samples | Accuracy | Weighted F1 | Macro F1 | Correct | Incorrect |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1 (VPN Detection)** | 59,706 | **93.40%** | **93.51%** (Binary F1) | N/A | N/A | N/A |
| **Hierarchical (End-to-End)** | 59,706 | **85.55%** | **85.63%** | **83.42%** | **51,077** | **8,629** |

---

## 24. Missing Information / Uncertainties

- **Missing Information**: Model training hyperparameters, splits (train/val/test ratio), and dataset collection source/environment details.
- **Why it matters**: Crucial for evaluating model generalization, bias, reproducibility of training, and understanding potential overfitting.
- **Where we searched**: Explored all codebase modules, configurations, and documentation files.
- **What to provide manually**: Details on dataset origin, data splitting strategy, and hyperparameter grids used during individual model training.

---

## 25. Recommended 25–30 Page Report Structure

1. **Abstract**: Core metrics (Stage-1 Accuracy: 93.40%, E2E Accuracy: 85.55%).
2. **Introduction**: Problem of encrypted traffic and hierarchical classification.
3. **Methodology**: Detailed routing flow, feature engineering (23 metrics), and scaling.
4. **Experimental Results**: Analysis of the E2E classification report and the [hierarchical_confusion_matrix.png](file:///d:/IISc/vpn_project/results/hierarchical_confusion_matrix.png).
5. **Deployment & Dashboard**: Streamlit interface pages, batch prediction logic, and export options.
6. **Discussion**: Error propagation, limits of offline evaluation, and data leakage warning.
7. **Conclusion & Future Work**: SHAP, FastAPI, and Docker scaling.
