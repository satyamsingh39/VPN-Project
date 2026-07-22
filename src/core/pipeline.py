import time
from pathlib import Path
from typing import Union, Tuple, Dict, Any
import pandas as pd
import numpy as np

from src.models.vpn_detector import VPNDetector
from src.models.vpn_classifier import VPNClassifier
from src.models.nonvpn_classifier import NonVPNClassifier

class PredictionPipeline:
    """
    Prediction Pipeline that orchestrates:
    Input -> VPN Detector -> VPN/Non-VPN Classifier -> Unified Outputs
    """
    def __init__(self):
        # Load model classes only once during initialization
        self.detector = VPNDetector()
        self.vpn_classifier = VPNClassifier()
        self.nonvpn_classifier = NonVPNClassifier()
        
        # Placeholders for metrics and statistics
        self.metrics: Dict[str, Any] = {}
        self.traffic_stats: pd.DataFrame = pd.DataFrame()
        self.application_stats: pd.DataFrame = pd.DataFrame()

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Runs the full prediction pipeline on a pandas DataFrame.
        Preserves all original input columns and appends predictions.

        Args:
            data (pd.DataFrame): Input DataFrame containing features.

        Returns:
            pd.DataFrame: DataFrame with original features and appended predictions.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame.")

        start_time = time.perf_counter()

        if data.empty:
            empty_df = data.copy()
            for col in ["Traffic Type", "Traffic Confidence", "Application", "Application Confidence"]:
                empty_df[col] = pd.Series(dtype=object)
            
            # Setup metrics and stats for empty input
            self.metrics = {
                "total_time": 0.0,
                "records_processed": 0,
                "avg_time_per_record": 0.0
            }
            self.traffic_stats = pd.DataFrame(columns=["Traffic Type", "Count"])
            self.application_stats = pd.DataFrame(columns=["Application", "Count"])
            return empty_df

        # Validate that the detector feature columns exist in the incoming data
        missing_cols = [col for col in self.detector.feature_columns if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required feature columns in input: {missing_cols}")

        # Predict traffic type (VPN vs. Non-VPN)
        traffic_preds, traffic_confs = self.detector.predict(data)

        # Initialize output arrays
        n_samples = len(data)
        traffic_types = ["" for _ in range(n_samples)]
        app_names = ["" for _ in range(n_samples)]
        app_confs = [0.0 for _ in range(n_samples)]

        # Get indices for VPN (1) and Non-VPN (0) samples
        vpn_indices = np.where(traffic_preds == 1)[0]
        nonvpn_indices = np.where(traffic_preds == 0)[0]

        # Process VPN samples
        if len(vpn_indices) > 0:
            vpn_df = data.iloc[vpn_indices]
            vpn_apps, vpn_app_confs = self.vpn_classifier.predict(vpn_df)
            for idx, app, conf in zip(vpn_indices, vpn_apps, vpn_app_confs):
                traffic_types[idx] = "VPN"
                app_names[idx] = app
                app_confs[idx] = conf

        # Process Non-VPN samples
        if len(nonvpn_indices) > 0:
            nonvpn_df = data.iloc[nonvpn_indices]
            nonvpn_apps, nonvpn_app_confs = self.nonvpn_classifier.predict(nonvpn_df)
            for idx, app, conf in zip(nonvpn_indices, nonvpn_apps, nonvpn_app_confs):
                traffic_types[idx] = "Non-VPN"
                app_names[idx] = app
                app_confs[idx] = conf

        # Construct result DataFrame keeping original input columns
        result_df = data.copy()
        result_df["Traffic Type"] = traffic_types
        result_df["Traffic Confidence"] = traffic_confs
        result_df["Application"] = app_names
        result_df["Application Confidence"] = app_confs

        # End timing
        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_time = total_time / n_samples

        # Save metrics
        self.metrics = {
            "total_time": total_time,
            "records_processed": n_samples,
            "avg_time_per_record": avg_time
        }

        # Calculate statistics
        traffic_counts = result_df["Traffic Type"].value_counts()
        self.traffic_stats = pd.DataFrame({
            "Traffic Type": traffic_counts.index,
            "Count": traffic_counts.values
        })

        app_counts = result_df["Application"].value_counts()
        self.application_stats = pd.DataFrame({
            "Application": app_counts.index,
            "Count": app_counts.values
        })

        # Clean console output
        print("=========================================")
        print("Prediction Pipeline Completed")
        print("=========================================")
        print(f"Records Processed : {n_samples}")
        print(f"VPN Flows         : {len(vpn_indices)}")
        print(f"Non-VPN Flows     : {len(nonvpn_indices)}")
        print(f"Prediction Time   : {total_time:.3f} sec")
        print("=========================================\n")

        print("======================================")
        print("Prediction Summary")
        print("======================================")
        print(f"Records Processed : {n_samples}")
        print(f"Prediction Time   : {total_time:.2f} seconds")
        print(f"Average / Record  : {avg_time:.6f} sec")
        print("======================================\n")

        return result_df

    def predict_csv(self, csv_path: Union[str, Path]) -> Tuple[pd.DataFrame, Dict[str, Any], pd.DataFrame, pd.DataFrame]:
        """
        Loads a CSV file, runs the prediction pipeline, and returns prediction details.

        Args:
            csv_path (Union[str, Path]): Path to the CSV file.

        Returns:
            Tuple[pd.DataFrame, Dict[str, Any], pd.DataFrame, pd.DataFrame]:
                - results_dataframe: DataFrame with all original + prediction columns
                - prediction_summary: Dict of metrics
                - traffic_statistics: DataFrame of traffic type value counts
                - application_statistics: DataFrame of application value counts
        """
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found at: {path}")

        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise ValueError(f"Failed to read invalid or malformed CSV file: {e}")

        results_df = self.predict(df)
        return results_df, self.metrics, self.traffic_stats, self.application_stats
