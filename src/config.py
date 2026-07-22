from pathlib import Path

# Project root path (d:\IISc\vpn_project)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Top level directories
MODELS_DIR = PROJECT_ROOT / "models"
DATASETS_DIR = PROJECT_ROOT / "datasets"

# Specific model directories
VPN_DETECTOR_DIR = MODELS_DIR / "vpn_detector"
VPN_CLASSIFIER_DIR = MODELS_DIR / "vpn_application"
NONVPN_CLASSIFIER_DIR = MODELS_DIR / "nonvpn_application"

# Specific datasets
VPN_DATASET_PATH = DATASETS_DIR / "vpn_only_dataset.csv"
NONVPN_DATASET_PATH = DATASETS_DIR / "nonvpn_only_dataset.csv"
FULL_DATASET_PATH = DATASETS_DIR / "dataset.csv"
