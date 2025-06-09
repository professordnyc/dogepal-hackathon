import streamlit as st
from pathlib import Path
import sys
import os

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set page config
st.set_page_config(
    page_title="DOGEPAL - Spending Insights",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .recommendation-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
    }
    .recommendation-card.high {
        border-left-color: #f44336;
    }
    .recommendation-card.medium {
        border-left-color: #ff9800;
    }
    .recommendation-card.low {
        border-left-color: #2196F3;
    }
</style>
""", unsafe_allow_html=True)

# Import pages
from pages import dashboard, spending_analysis, recommendations

# Sidebar navigation
st.sidebar.title("DOGEPAL")
st.sidebar.markdown("---")

# Add logo or app description
st.sidebar.image(
    "https://img.icons8.com/color/96/000000/money-bag-euro.png",
    width=80
)
st.sidebar.markdown("### Local Spending Recommendation Engine")
st.sidebar.markdown("Gain insights and optimize your spending with AI-powered recommendations.")
st.sidebar.markdown("---")

# Page selection
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Spending Analysis", "Recommendations"],
    index=0
)

# Display the selected page
if page == "Dashboard":
    dashboard.show()
elif page == "Spending Analysis":
    spending_analysis.show()
else:
    recommendations.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 1rem;">
        <p>Built with ❤️ for HP AI Studio Hackathon</p>
        <p style="font-size: 0.8rem; color: #666;">v0.1.0</p>
    </div>
    """,
    unsafe_allow_html=True
)
