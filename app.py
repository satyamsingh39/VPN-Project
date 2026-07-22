import streamlit as st

# 1. Setup page config (MUST be called first)
st.set_page_config(
    page_title="Encrypted Traffic Classifier",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.ui.sidebar import render_sidebar
from src.ui.home import render_home
from src.ui.prediction import render_prediction
from src.ui.about import render_about
from src.core.pipeline import PredictionPipeline

# 2. Initialize PredictionPipeline in session state so it only loads once
if "pipeline" not in st.session_state:
    try:
        st.session_state["pipeline"] = PredictionPipeline()
        st.session_state["pipeline_ready"] = True
        st.session_state["pipeline_error"] = None
    except Exception as e:
        st.session_state["pipeline_ready"] = False
        st.session_state["pipeline_error"] = str(e)

# 3. Render sidebar navigation
page = render_sidebar()

# 4. Route page rendering
if page == "Home":
    render_home()
elif page == "Prediction":
    render_prediction()
elif page == "About":
    render_about()
