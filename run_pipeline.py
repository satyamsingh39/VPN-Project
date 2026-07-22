import pandas as pd
from pathlib import Path
from src.core.pipeline import PredictionPipeline
from src.config import VPN_DATASET_PATH

def main():
    print("=========================================")
    print("Starting Upgraded ML Prediction Pipeline")
    print("=========================================\n")

    # Initialize the pipeline
    print("Initializing PredictionPipeline...")
    pipeline = PredictionPipeline()
    print("Pipeline initialized.\n")

    # Run predictions on a CSV file
    print(f"Running predictions on: {VPN_DATASET_PATH}")
    try:
        # Run predict_csv
        results_df, summary, traffic_stats, app_stats = pipeline.predict_csv(VPN_DATASET_PATH)
        
        # 1. Print metrics summary
        print("--- 1. Performance Summary (Exposed Dict) ---")
        print(summary)
        print()

        # 2. Print traffic statistics
        print("--- 2. Traffic Statistics ---")
        print(traffic_stats.to_string(index=False))
        print()

        # 3. Print application statistics
        print("--- 3. Application Statistics ---")
        print(app_stats.to_string(index=False))
        print()

        # 4. Show first 5 rows of output DataFrame (to show original + prediction columns)
        print("--- 4. First 5 Rows of Final Output (original + prediction columns) ---")
        print(results_df.head())
        print()

        # 5. Save final predictions DataFrame to results/predictions.csv
        results_dir = Path(__file__).resolve().parent / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        output_csv_path = results_dir / "predictions.csv"
        results_df.to_csv(output_csv_path, index=False)
        print(f"--- 5. Successfully saved results to: {output_csv_path} ---")
        
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    main()
