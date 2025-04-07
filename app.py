import streamlit as st
from pyweb3d import ThreeJS
import time
from streamlit_extras.let_it_rain import rain

# Page configuration
st.set_page_config(
    page_title="3D Calculator",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
def load_css():
    with open("assets/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# 3D Background using Three.js
def threejs_background():
    threejs_html = """
    <canvas id="bgCanvas" style="position:fixed;top:0;left:0;z-index:-1;"></canvas>
    <script src="assets/threejs-background.js"></script>
    """
    st.components.v1.html(threejs_html, height=0)

threejs_background()

# Calculator UI in glass container
with st.container():
    st.markdown("""
    <div class="calculator-header">
        <h1>🌀 3D Calculator</h1>
        <p class="subheader">Calculate in a cosmic dimension</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            num1 = st.number_input("First Number", value=0.0, step=0.1, key="num1")
        with col2:
            num2 = st.number_input("Second Number", value=0.0, step=0.1, key="num2")

        operation = st.radio(
            "Select Operation",
            ["➕ Addition", "➖ Subtraction", "✖️ Multiplication", "➗ Division"],
            horizontal=True
        )

        if st.button("Calculate", key="calculate", type="primary", use_container_width=True):
            with st.spinner('Warping through dimensions...'):
                time.sleep(0.8)  # Simulate cosmic calculation
                
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
                    
                    # Cosmic celebration
                    rain(
                        emoji="🌌",
                        font_size=40,
                        falling_speed=3,
                        animation_length=2,
                    )
                    
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
                    st.error("Black hole detected! Division by zero!", icon="🕳️")
                except Exception as e:
                    st.error(f"Cosmic anomaly: {str(e)}", icon="☄️")

        st.markdown('</div>', unsafe_allow_html=True)

# Floating features section
st.markdown("""
<div class="features">
    <h3>🌠 Cosmic Features</h3>
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🪐</div>
            <h4>3D Universe</h4>
            <p>Interactive cosmic background</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚛️</div>
            <h4>Quantum Speed</h4>
            <p>Faster than light calculations</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🌌</div>
            <h4>Stellar Effects</h4>
            <p>Galactic animations</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
