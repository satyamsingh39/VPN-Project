import json
from pathlib import Path
from typing import Any
import joblib

def load_json(filepath: Path) -> Any:
    """
    Loads a JSON file and returns its content.

    Args:
        filepath (Path): The pathlib Path to the JSON file.

    Returns:
        Any: The parsed JSON content.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"JSON file not found at: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_pickle(filepath: Path) -> Any:
    """
    Loads a pickle file using joblib.

    Args:
        filepath (Path): The pathlib Path to the pickle file.

    Returns:
        Any: The loaded Python object (model, scaler, label encoder, etc.).

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Pickle file not found at: {filepath}")
    return joblib.load(filepath)
