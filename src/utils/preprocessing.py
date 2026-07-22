import pandas as pd
from typing import List, Union, Dict, Any
from sklearn.preprocessing import StandardScaler

def preprocess_features(
    data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
    required_columns: List[str],
    scaler: StandardScaler
) -> pd.DataFrame:
    """
    Validates, filters, reorders, and scales input feature data.

    Args:
        data (Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]): Input feature data.
        required_columns (List[str]): Expected training feature columns in correct order.
        scaler (StandardScaler): Pre-trained and loaded scaler.

    Returns:
        pd.DataFrame: Scaled features in the exact expected order.

    Raises:
        TypeError: If data is not a DataFrame, dictionary, or list of dictionaries.
        ValueError: If required columns are missing from the input data.
    """
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise TypeError("Input data must be a pandas DataFrame, a dict, or a list of dicts.")

    # Validate missing columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required feature columns: {missing_cols}")

    # Keep only required columns and reorder them exactly like training
    df_filtered = df[required_columns]

    # Apply scaler
    scaled_arr = scaler.transform(df_filtered)
    
    # Return as a DataFrame to keep the structure clear
    return pd.DataFrame(scaled_arr, columns=required_columns, index=df_filtered.index)
