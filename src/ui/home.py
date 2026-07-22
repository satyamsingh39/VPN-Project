import streamlit as st

def render_home() -> None:
    """
    Renders the Home page of the Streamlit application.
    """
    st.title(" Hierarchical Encrypted Network Traffic Classification")
    
    st.markdown(
        "This project implements a multi-tier machine learning classification system designed to analyze "
        "encrypted network flow telemetry. By extracting statistical characteristics such as packet sizing, "
        "flow duration, and inter-arrival times, the system identifies whether a traffic flow is routed through "
        "a VPN and subsequently pinpoints the specific application generating the activity."
    )

    st.markdown("### 📊 Pipeline Architecture Workflow")
    st.code(
        """
      Network Traffic
             │
             ▼
       VPN Detector
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
     VPN        Non-VPN
      │             │
      ▼             ▼
     VPN App     NonVPN App
      │             │
      └──────┬──────┘
             ▼
      Final Prediction
        """,
        language="text"
    )

    st.markdown("### 🛠️ Configured ML Estimators")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(
            "**VPN Detector**\n\n"
            "Estimator: `Random Forest`\n\n"
            "Task: Binary Classifier"
        )
    with col2:
        st.success(
            "**VPN Application Classifier**\n\n"
            "Estimator: `XGBoost`\n\n"
            "Task: Multiclass Classifier"
        )
    with col3:
        st.warning(
            "**Non VPN Application Classifier**\n\n"
            "Estimator: `XGBoost`\n\n"
            "Task: Multiclass Classifier"
        )

    st.markdown("---")
    st.markdown("### 🚀 Project Highlights")
    st.markdown(
        "- **Hierarchical Prediction Pipeline**: Routes flows intelligently to optimize application-level classification accuracy.\n"
        "- **Automatic Feature Validation**: Validates telemetry flow columns dynamically, ignoring irrelevant columns.\n"
        "- **Confidence Scores**: Exposes probability outputs for both traffic detection and application classification layers.\n"
        "- **Batch CSV Prediction**: Handles thousands of flows simultaneously in a vectorized manner for rapid execution.\n"
        "- **Dynamic Feature Loading**: Generates input fields dynamically based on underlying model schema definitions.\n"
        "- **Fast Inference**: Designed with optimized backend loaders ensuring sub-millisecond classification per record."
    )
