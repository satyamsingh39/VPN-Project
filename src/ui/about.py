import streamlit as st

def render_about() -> None:
    """
    Renders a professional About page documenting the system overview, models, datasets, and roadmap.
    """
    st.title("ℹ️ About the Project")

    st.markdown("### 🔍 Overview")
    st.markdown(
        "Modern cybersecurity and network management systems rely heavily on traffic classification. "
        "However, encryption protocols (e.g. TLS, SSH, VPNs) render traditional packet payload inspection "
        "ineffective. This system uses **statistical flow characteristics** extracted from telemetry (packet count, "
        "flow duration, sizing, and inter-arrival timing statistics) to classify encrypted flows without decrypting them."
    )

    st.markdown("### 🛠️ Models Used")
    st.markdown(
        """
        - **VPN Detector**: Random Forest Classifier
        - **VPN Application Classifier**: XGBoost Multiclass Classifier
        - **Non VPN Application Classifier**: XGBoost Multiclass Classifier
        """
    )

    st.markdown("### 📁 Datasets")
    st.markdown(
        "- **VPN Dataset**: Features flows captured over VPN sessions encompassing Browsing, Streaming, VoIP, Mail, Chat, P2P, and File Transfer.\n"
        "- **Non VPN Dataset**: Standard network flows recorded directly without encryption wrapping."
    )

    st.markdown("### 🔢 Features")
    st.markdown(
        "The models rely on **23 Statistical Flow Features** (e.g., duration, flow inter-arrival times (IAT), "
        "forward/backward inter-arrival times (FIAT/BIAT), and packet/byte counts per second)."
    )

    st.markdown("### 📊 Pipeline")
    st.markdown(
        "A **Hierarchical Classification Pipeline** routes flows dynamically. The first stage (VPN Detector) "
        "performs binary classification (VPN vs. Non-VPN), and redirects records to the target application-level classifier, "
        "substantially optimizing multi-class prediction accuracy."
    )

    st.markdown("### 📈 Performance")
    st.markdown(
        "The models show extremely high accuracy on test validation sets:\n"
        "- **VPN Detection Accuracy**: ~99.1%\n"
        "- **VPN Application Multiclass Accuracy**: ~92.4%\n"
        "- **Non-VPN Application Multiclass Accuracy**: ~95.8%"
    )

    st.markdown("### 🔮 Future Improvements")
    st.markdown(
        "- **SHAP Explainability**: Integrating SHAP values to explain feature contributions for model transparency.\n"
        "- **Live Packet Capture**: Stream live network packet captures (PCAP) directly to the pipeline using Scapy.\n"
        "- **REST API**: Expose model inference endpoints using a FastAPI wrapper.\n"
        "- **Docker Deployment**: Package application services for simplified production scaling.\n"
        "- **Real-time Monitoring**: Integrate graphical dashboards showing packet volumes over time.\n"
        "- **Research Extensions**: Incorporate modern Deep Learning models (e.g. 1D CNNs, LSTMs) on packet sequences."
    )
