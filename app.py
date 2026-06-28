import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Chase Vault Card Tracker", layout="wide")

st.title("Chase Vault Card Tracker")
st.write("Track trading card values, compare eBay prices, and manage your inventory.")

card_name = st.text_input("Enter card name")
purchase_price = st.number_input("Purchase price", min_value=0.0, step=1.0)
current_price = st.number_input("Current market price", min_value=0.0, step=1.0)
quantity = st.number_input("Quantity", min_value=1, step=1)

if st.button("Analyze Card"):
    total_cost = purchase_price * quantity
    total_value = current_price * quantity
    profit_loss = total_value - total_cost

    if current_price > purchase_price * 1.25:
        status = "Sell"
    elif current_price < purchase_price * 0.85:
        status = "Buy/Hold"
    else:
        status = "Hold"

    st.subheader("Card Analysis")
    st.write(f"Total Cost: ${total_cost:.2f}")
    st.write(f"Current Value: ${total_value:.2f}")
    st.write(f"Profit/Loss: ${profit_loss:.2f}")
    st.write(f"Recommendation: {status}")

    df = pd.DataFrame({
        "Category": ["Cost", "Current Value"],
        "Amount": [total_cost, total_value]
    })

    fig = px.bar(df, x="Category", y="Amount", title="Card Value Comparison")
    st.plotly_chart(fig)
