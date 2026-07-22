from pathlib import Path
from typing import Union, Dict, Any, List, Tuple
import pandas as pd
import numpy as np

from src.utils.loader import load_json, load_pickle
from src.utils.preprocessing import preprocess_features
from src.config import VPN_DETECTOR_DIR

class VPNDetector:
    """
    VPN Detector wrapper. Automatically loads the random forest model,
    scaler, and feature columns to detect VPN vs. Non-VPN traffic.
    """
    def __init__(self, model_dir: Path = None):
        if model_dir is None:
            model_dir = VPN_DETECTOR_DIR
        
        self.model_dir = Path(model_dir)
        self.feature_columns = load_json(self.model_dir / "feature_columns.json")
        self.scaler = load_pickle(self.model_dir / "vpn_scaler.pkl")
        self.model = load_pickle(self.model_dir / "vpn_random_forest_model.pkl")

    def predict(
        self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predicts whether the given traffic flow is VPN or Non-VPN.

        Args:
            data (Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]): Input feature data.

        Returns:
            Tuple[np.ndarray, np.ndarray]:
                - predictions: Array of predicted labels (e.g. 0/1, True/False, or VPN/Non-VPN).
                - confidences: Array of confidence scores (highest probability for the predicted class).
        """
        # Preprocess features
        preprocessed_data = preprocess_features(data, self.feature_columns, self.scaler)
        
        # Predict classes
        predictions = self.model.predict(preprocessed_data.values)
        
        # Predict probabilities
        probabilities = self.model.predict_proba(preprocessed_data.values)
        
        # Confidence is the probability of the predicted class
        confidences = np.max(probabilities, axis=1)
        
        return predictions, confidences
