import streamlit as st

# Configure the page
st.set_page_config(
    page_title="Simple Calculator",
    page_icon="🧮",
    layout="centered"
)

# Title of the app
st.title("🧮 Simple Calculator")

# Input fields for numbers
col1, col2 = st.columns(2)
with col1:
    num1 = st.number_input("Enter first number", value=0.0, step=0.1)
with col2:
    num2 = st.number_input("Enter second number", value=0.0, step=0.1)

# Operation selection
operation = st.selectbox(
    "Select operation",
    ["Addition", "Subtraction", "Multiplication", "Division"],
    index=0
)

# Calculate button
calculate = st.button("Calculate", type="primary")

def calculate_result(a, b, op):
    """Perform calculation based on operation"""
    if op == "Addition":
        return a + b
    elif op == "Subtraction":
        return a - b
    elif op == "Multiplication":
        return a * b
    elif op == "Division":
        if b == 0:
            raise ZeroDivisionError("Division by zero is not allowed")
        return a / b
    else:
        raise ValueError("Invalid operation")

# Display result when calculate is clicked
if calculate:
    try:
        result = calculate_result(num1, num2, operation)
        st.success(f"**Result:** {num1} {operation[:1]} {num2} = **{result}**")
    except Exception as e:
        st.error(f"🚨 {str(e)}")

# Add some instructions
st.markdown("---")
st.markdown("""
### How to use:
1. Enter two numbers
2. Select an operation
3. Click the Calculate button
""")

# Footer
st.caption("Made with Streamlit · [Deploy your own](https://streamlit.io/)")
