import pandas as pd
from pathlib import Path
from src.models.vpn_detector import VPNDetector
from src.models.vpn_classifier import VPNClassifier
from src.models.nonvpn_classifier import NonVPNClassifier
from src.config import VPN_DATASET_PATH, NONVPN_DATASET_PATH

def main():
    print("=========================================")
    print("Starting ML Models Backend Verification")
    print("=========================================\n")

    # Load small subsets of data
    print("Loading test samples...")
    try:
        vpn_df = pd.read_csv(VPN_DATASET_PATH, nrows=5)
        nonvpn_df = pd.read_csv(NONVPN_DATASET_PATH, nrows=5)
        print("Datasets loaded successfully.")
    except Exception as e:
        print(f"Error loading datasets: {e}")
        return

    # 1. Test VPN Detector
    print("\n--- 1. Testing VPNDetector ---")
    detector = VPNDetector()
    
    # Test with a VPN sample
    vpn_sample = vpn_df.iloc[[0]]
    pred_vpn, conf_vpn = detector.predict(vpn_sample)
    print(f"VPN Sample actual vpn_label: {vpn_sample['vpn_label'].values[0]}")
    print(f"Detector Prediction: {pred_vpn[0]} | Confidence: {conf_vpn[0]:.4f}")

    # Test with a Non-VPN sample
    nonvpn_sample = nonvpn_df.iloc[[0]]
    pred_nvpn, conf_nvpn = detector.predict(nonvpn_sample)
    print(f"Non-VPN Sample actual vpn_label: {nonvpn_sample['vpn_label'].values[0]}")
    print(f"Detector Prediction: {pred_nvpn[0]} | Confidence: {conf_nvpn[0]:.4f}")

    # 2. Test VPN Classifier
    print("\n--- 2. Testing VPNClassifier ---")
    vpn_classifier = VPNClassifier()
    # Classify the VPN samples
    pred_vpn_apps, conf_vpn_apps = vpn_classifier.predict(vpn_df)
    for i in range(len(vpn_df)):
        actual_app = vpn_df.iloc[i].get('traffic_type', 'N/A')
        print(f"Sample {i+1} | Actual Application: {actual_app} | Predicted: {pred_vpn_apps[i]} | Confidence: {conf_vpn_apps[i]:.4f}")

    # 3. Test Non-VPN Classifier
    print("\n--- 3. Testing NonVPNClassifier ---")
    nonvpn_classifier = NonVPNClassifier()
    # Classify the Non-VPN samples
    pred_nvpn_apps, conf_nvpn_apps = nonvpn_classifier.predict(nonvpn_df)
    for i in range(len(nonvpn_df)):
        actual_app = nonvpn_df.iloc[i].get('traffic_type', 'N/A')
        print(f"Sample {i+1} | Actual Application: {actual_app} | Predicted: {pred_nvpn_apps[i]} | Confidence: {conf_nvpn_apps[i]:.4f}")

    # 4. Column validation check
    print("\n--- 4. Column Validation Check (Error Handling) ---")
    invalid_sample = vpn_sample.drop(columns=['duration'])
    try:
        detector.predict(invalid_sample)
        print("ERROR: Predictor did not raise ValueError on missing column!")
    except ValueError as ve:
        print(f"SUCCESS: Correctly caught missing column: {ve}")

if __name__ == "__main__":
    main()
