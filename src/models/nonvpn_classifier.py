from pathlib import Path
from typing import Union, Dict, Any, List, Tuple
import pandas as pd
import numpy as np

from src.utils.loader import load_json, load_pickle
from src.utils.preprocessing import preprocess_features
from src.config import NONVPN_CLASSIFIER_DIR

class NonVPNClassifier:
    """
    Non-VPN Classifier wrapper. Automatically loads the application classification model,
    scaler, label encoder, and feature columns to classify non-VPN traffic into specific applications.
    """
    def __init__(self, model_dir: Path = None):
        if model_dir is None:
            model_dir = NONVPN_CLASSIFIER_DIR
        
        self.model_dir = Path(model_dir)
        self.feature_columns = load_json(self.model_dir / "feature_columns.json")
        self.scaler = load_pickle(self.model_dir / "nonvpn_application_scaler.pkl")
        self.label_encoder = load_pickle(self.model_dir / "nonvpn_application_label_encoder.pkl")
        self.model = load_pickle(self.model_dir / "best_nonvpn_application_model.pkl")

    def predict(
        self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Classifies non-VPN traffic flow into specific applications.

        Args:
            data (Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]): Input feature data.

        Returns:
            Tuple[np.ndarray, np.ndarray]:
                - predictions: Array of predicted application string names.
                - confidences: Array of confidence scores (highest probability for the predicted class).
        """
        # Preprocess features
        preprocessed_data = preprocess_features(data, self.feature_columns, self.scaler)
        
        # Predict encoded classes
        predictions_encoded = self.model.predict(preprocessed_data.values)
        
        # Decode classes to string labels
        predictions = self.label_encoder.inverse_transform(predictions_encoded)
        
        # Predict probabilities
        probabilities = self.model.predict_proba(preprocessed_data.values)
        
        # Confidence is the probability of the predicted class
        confidences = np.max(probabilities, axis=1)
        
        return predictions, confidences
