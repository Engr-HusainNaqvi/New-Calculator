import streamlit as st
from PIL import Image
import time
from streamlit_extras.let_it_rain import rain

# Page configuration
st.set_page_config(
    page_title="Premium Calculator",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
def load_css():
    with open("assets/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Background image
def set_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# Calculator UI
with st.container():
    st.markdown("""
    <div class="calculator-header">
        <h1>✨ Premium Calculator</h1>
        <p class="subheader">Experience mathematical elegance</p>
    </div>
    """, unsafe_allow_html=True)

    # Glassmorphism card effect
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            num1 = st.number_input("First Number", value=0.0, step=0.1, key="num1",
                                 help="Enter your first operand")
        with col2:
            num2 = st.number_input("Second Number", value=0.0, step=0.1, key="num2",
                                 help="Enter your second operand")

        # Operation selection with icons
        operation = st.radio(
            "Select Operation",
            ["➕ Addition", "➖ Subtraction", "✖️ Multiplication", "➗ Division"],
            horizontal=True,
            label_visibility="visible"
        )

        # Animated calculate button
        if st.button("Calculate", key="calculate", type="primary", use_container_width=True):
            with st.spinner('Calculating...'):
                time.sleep(0.5)  # Simulate processing
                
                try:
                    op_symbol = operation[0]
                    if "Addition" in operation:
                        result = num1 + num2
                    elif "Subtraction" in operation:
                        result = num1 - num2
                    elif "Multiplication" in operation:
                        result = num1 * num2
                    elif "Division" in operation:
                        if num2 == 0:
                            raise ZeroDivisionError
                        result = num1 / num2
                    
                    # Celebration animation
                    rain(
                        emoji="✨",
                        font_size=30,
                        falling_speed=5,
                        animation_length=1,
                    )
                    
                    # Display result with animation
                    st.markdown(f"""
                    <div class="result-container">
                        <div class="calculation">
                            {num1} {op_symbol} {num2} =
                        </div>
                        <div class="result">
                            {result:,.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except ZeroDivisionError:
                    st.error("Division by zero is not allowed!", icon="🚨")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}", icon="⚠️")

        st.markdown('</div>', unsafe_allow_html=True)

# Features section
st.markdown("""
<div class="features">
    <h3>🌟 Premium Features</h3>
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h4>Lightning Fast</h4>
            <p>Instant calculations with smooth animations</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <h4>Beautiful UI</h4>
            <p>Modern glassmorphism design</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h4>Error Protected</h4>
            <p>Handles all edge cases gracefully</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
