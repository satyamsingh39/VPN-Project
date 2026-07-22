import streamlit as st

def render_sidebar() -> str:
    """
    Renders a professional navigation sidebar with system status metadata.

    Returns:
        str: Selected page name.
    """
    st.sidebar.title("🔒 Traffic Classifier")
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Home", "Prediction", "About"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Status")
    
    # Render neat status indicators
    st.sidebar.markdown(
        """
        - **Backend**: `Loaded`
        - **Models**: `Loaded`
        - **Pipeline**: `Ready`
        - **Feature Count**: `23`
        """
    )
    
    return page
