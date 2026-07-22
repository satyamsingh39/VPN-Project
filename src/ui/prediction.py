import time
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

from src.core.pipeline import PredictionPipeline

def render_prediction() -> None:
    """
    Renders the Inference & Analysis Prediction page.
    """
    st.title("🔍 Inference & Analysis")

    if "pipeline" not in st.session_state or not st.session_state.get("pipeline_ready", False):
        st.error("Prediction pipeline is not initialized or failed to load. Please check logs.")
        if "pipeline_error" in st.session_state and st.session_state["pipeline_error"]:
            st.code(st.session_state["pipeline_error"])
        return

    pipeline: PredictionPipeline = st.session_state["pipeline"]
    feature_columns = pipeline.detector.feature_columns

    tab1, tab2 = st.tabs(["📝 Manual Prediction", "📁 Batch Prediction"])

    # Feature groups specification
    feature_groups = {
        "Flow Features": ["duration", "total_fiat", "total_biat"],
        "Timing Features": ["min_fiat", "min_biat", "max_fiat", "max_biat", "mean_fiat", "mean_biat"],
        "Flow IAT": ["min_flowiat", "max_flowiat", "mean_flowiat", "std_flowiat"],
        "Active Time": ["min_active", "mean_active", "max_active", "std_active"],
        "Idle Time": ["min_idle", "mean_idle", "max_idle", "std_idle"],
        "Flow Statistics": ["flowPktsPerSecond", "flowBytesPerSecond"]
    }

    with tab1:
        st.subheader("Manual Feature Input")
        st.markdown("Supply custom telemetry flow features grouped by their parameters:")

        inputs = {}
        
        # Render inputs grouped logically
        for group_name, features in feature_groups.items():
            st.markdown(f"##### {group_name}")
            actual_features = [f for f in features if f in feature_columns]
            if not actual_features:
                continue
            
            cols = st.columns(3)
            for idx, feature in enumerate(actual_features):
                col_target = cols[idx % 3]
                inputs[feature] = col_target.number_input(
                    label=feature,
                    value=0.0,
                    step=0.01,
                    format="%.6f",
                    key=f"manual_{feature}"
                )
            st.markdown("---")

        if st.button("Predict Single Sample", type="primary"):
            with st.spinner("Classifying sample..."):
                try:
                    # Construct single-row DataFrame
                    input_df = pd.DataFrame([inputs])
                    
                    # Run prediction
                    start_time = time.perf_counter()
                    result_df = pipeline.predict(input_df)
                    exec_time = time.perf_counter() - start_time
                    
                    # Extract prediction details
                    traffic_type = result_df["Traffic Type"].values[0]
                    traffic_conf = result_df["Traffic Confidence"].values[0]
                    app_name = result_df["Application"].values[0]
                    app_conf = result_df["Application Confidence"].values[0]
                    
                    st.success("Prediction complete!")
                    
                    # Metric cards layout
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.metric("Traffic Type", traffic_type)
                    m2.metric("Traffic Confidence", f"{traffic_conf * 100:.2f} %")
                    m3.metric("Application", app_name)
                    m4.metric("Application Confidence", f"{app_conf * 100:.2f} %")
                    m5.metric("Prediction Time", f"{exec_time:.3f} seconds")
                    
                    # Expandable details
                    with st.expander("📝 Prediction Details"):
                        st.markdown(
                            f"""
                            - **Model Used (Level 1)**: VPN Detector (Random Forest)
                            - **Model Used (Level 2)**: { "VPN Classifier (XGBoost)" if traffic_type == "VPN" else "Non-VPN Classifier (XGBoost)" }
                            - **Total Features Used**: {len(feature_columns)}
                            - **Scaling**: StandardScaler
                            - **Prediction Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            """
                        )
                except Exception as e:
                    st.error(f"Prediction Failed: {e}")

    with tab2:
        st.subheader("Batch Prediction from CSV")
        st.markdown("Upload telemetry flow data in a CSV file format to perform bulk predictions.")
        
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        
        if uploaded_file is not None:
            try:
                # Load DataFrame
                df = pd.read_csv(uploaded_file)
                st.info(f"Loaded CSV file with {len(df)} rows and {len(df.columns)} columns.")
                
                # Check for missing feature columns before previewing/predicting
                missing = [col for col in feature_columns if col not in df.columns]
                if missing:
                    st.error(f"Invalid columns! The uploaded CSV is missing: {missing}")
                else:
                    st.markdown("#### Input Data Preview (First 5 Rows)")
                    st.dataframe(df.head())
                    
                    if st.button("Run Batch Prediction", type="primary"):
                        with st.spinner("Processing batch predictions..."):
                            try:
                                # Run pipeline
                                results_df = pipeline.predict(df)
                                
                                st.success("Batch prediction completed successfully!")
                                
                                # Gather summary counts
                                vpn_count = int(pipeline.traffic_stats.loc[pipeline.traffic_stats["Traffic Type"] == "VPN", "Count"].values[0]) if "VPN" in pipeline.traffic_stats["Traffic Type"].values else 0
                                non_vpn_count = int(pipeline.traffic_stats.loc[pipeline.traffic_stats["Traffic Type"] == "Non-VPN", "Count"].values[0]) if "Non-VPN" in pipeline.traffic_stats["Traffic Type"].values else 0
                                
                                # Show metric cards summarizing results
                                p1, p2, p3, p4, p5 = st.columns(5)
                                p1.metric("Records Processed", len(results_df))
                                p2.metric("VPN Count", vpn_count)
                                p3.metric("Non VPN Count", non_vpn_count)
                                p4.metric("Prediction Time", f"{pipeline.metrics['total_time']:.2f} s")
                                p5.metric("Avg Time per Record", f"{pipeline.metrics['avg_time_per_record'] * 1000:.4f} ms")
                                
                                # Distributions Charts
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.markdown("#### Traffic Type Distribution")
                                    # Create Series for charting
                                    t_chart_data = pipeline.traffic_stats.set_index("Traffic Type")["Count"]
                                    st.bar_chart(t_chart_data)
                                    
                                with c2:
                                    st.markdown("#### Application Distribution")
                                    a_chart_data = pipeline.application_stats.set_index("Application")["Count"]
                                    st.bar_chart(a_chart_data)

                                # Full dataframe preview (first 10 rows)
                                st.markdown("#### Predictions Output (First 10 Rows)")
                                st.dataframe(results_df.head(10))

                                # Save predictions inside results/predictions.csv
                                results_dir = Path(__file__).resolve().parents[2] / "results"
                                results_dir.mkdir(parents=True, exist_ok=True)
                                output_csv_path = results_dir / "predictions.csv"
                                results_df.to_csv(output_csv_path, index=False)
                                
                                # Download CSV button
                                csv_data = results_df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="📥 Download Predictions CSV",
                                    data=csv_data,
                                    file_name="predictions.csv",
                                    mime="text/csv"
                                )
                                st.info(f"Predictions auto-saved to: {output_csv_path}")
                            except Exception as ex:
                                st.error(f"Inference error during batch run: {ex}")
            except Exception as e:
                st.error(f"Malformed CSV file error: {e}")
