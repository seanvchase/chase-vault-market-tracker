import streamlit as st
import pandas as pd
import plotly.express as px

from services.ebay_api import search_ebay_cards
from services.recommendations import get_recommendation
from services.scanner import identify_card_from_image
from database.database import create_cards_table, add_card, get_all_cards, delete_card
from services.exporter import create_inventory_excel


create_cards_table()

st.set_page_config(page_title="Chase Vault Market Tracker", layout="wide")

st.title("Chase Vault Market Tracker")
st.write("Track trading card values, compare eBay prices, and manage your inventory.")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Inventory", "eBay Market Search", "Card Analysis", "AI Scanner"]
)
if page == "Dashboard":
    st.header("Dashboard")
    st.write("Welcome to your trading card market tracker.")

    st.metric("Portfolio Value", "$0.00")
    st.metric("Cards Tracked", "0")
    st.metric("Market Alerts", "0")

elif page == "eBay Market Search":
    st.header("eBay Market Search")

    card_name = st.text_input("Enter card name")

    if st.button("Search eBay"):
        results = search_ebay_cards(card_name)

        st.subheader("Sample eBay Results")

        for item in results:
            st.write(f"**{item['title']}**")
            st.write(f"Price: ${item['price']}")
            st.write(f"Condition: {item['condition']}")
            st.divider()

elif page == "Card Analysis":
    st.header("Card Analysis")

    card_name = st.text_input("Card name")
    purchase_price = st.number_input("Purchase price", min_value=0.0, step=1.0)
    current_price = st.number_input("Current market price", min_value=0.0, step=1.0)
    quantity = st.number_input("Quantity", min_value=1, step=1)

    if st.button("Analyze Card"):
        total_cost = purchase_price * quantity
        total_value = current_price * quantity
        profit_loss = total_value - total_cost
        recommendation = get_recommendation(purchase_price, current_price)

        st.subheader("Card Analysis Results")
        st.write(f"Card: {card_name}")
        st.write(f"Total Cost: ${total_cost:.2f}")
        st.write(f"Current Value: ${total_value:.2f}")
        st.write(f"Profit/Loss: ${profit_loss:.2f}")
        st.write(f"Recommendation: {recommendation}")

        df = pd.DataFrame({
            "Category": ["Cost", "Current Value"],
            "Amount": [total_cost, total_value]
        })

        fig = px.bar(df, x="Category", y="Amount", title="Card Value Comparison")
        st.plotly_chart(fig)

elif page == "AI Scanner":
    st.header("AI Card Scanner")

    uploaded_image = st.file_uploader("Upload a card image", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Card", use_container_width=True)

        if st.button("Scan Card"):
            result = identify_card_from_image(uploaded_image)

            st.subheader("Scan Result")
            st.write(f"Name: {result['name']}")
            st.write(f"Game: {result['game']}")
            st.write(f"Set: {result['set']}")
            st.write(f"Card Number: {result['card_number']}")
            st.write(f"Rarity: {result['rarity']}")
            st.write(f"Condition Estimate: {result['condition_estimate']}")

elif page == "Inventory":
    st.header("Card Inventory")

    st.subheader("Add a Card")

    with st.form("add_card_form"):
        name = st.text_input("Card Name")
        game = st.selectbox("Game", ["Pokemon", "One Piece", "Sports", "Magic", "Yu-Gi-Oh", "Other"])
        set_name = st.text_input("Set Name")
        card_number = st.text_input("Card Number")
        condition = st.selectbox("Condition", ["Raw", "Near Mint", "Lightly Played", "Moderately Played", "Damaged", "Graded"])
        quantity = st.number_input("Quantity", min_value=1, step=1)
        purchase_price = st.number_input("Purchase Price", min_value=0.0, step=1.0)
        current_value = st.number_input("Current Market Value", min_value=0.0, step=1.0)

        submitted = st.form_submit_button("Add Card")

        if submitted:
            add_card(
                name,
                game,
                set_name,
                card_number,
                condition,
                quantity,
                purchase_price,
                current_value
            )
            st.success(f"{name} added to inventory.")

    st.divider()

    st.subheader("Current Inventory")

    cards = get_all_cards()

    if cards:
        inventory_data = []

        for card in cards:
            card_id, name, game, set_name, card_number, condition, quantity, purchase_price, current_value = card

            total_cost = quantity * purchase_price
            total_value = quantity * current_value
            profit_loss = total_value - total_cost

            inventory_data.append({
                "ID": card_id,
                "Name": name,
                "Game": game,
                "Set": set_name,
                "Card Number": card_number,
                "Condition": condition,
                "Qty": quantity,
                "Paid Each": purchase_price,
                "Market Each": current_value,
                "Total Cost": total_cost,
                "Total Value": total_value,
                "Profit/Loss": profit_loss
            })

        st.dataframe(inventory_data, use_container_width=True)

        st.subheader("Delete a Card")
        card_id_to_delete = st.number_input("Enter card ID to delete", min_value=1, step=1)

        if st.button("Delete Card"):
            delete_card(card_id_to_delete)
            st.warning(f"Card ID {card_id_to_delete} deleted. Refresh the page to update the table.")

    else:
        st.info("No cards in inventory yet.")
        
elif page == "Inventory":
    st.header("Card Inventory")

    st.subheader("Add a Card")

    with st.form("add_card_form"):
        name = st.text_input("Card Name")
        game = st.selectbox("Game", ["Pokemon", "One Piece", "Sports", "Magic", "Yu-Gi-Oh", "Other"])
        set_name = st.text_input("Set Name")
        card_number = st.text_input("Card Number")
        condition = st.selectbox("Condition", ["Raw", "Near Mint", "Lightly Played", "Moderately Played", "Damaged", "Graded"])
        quantity = st.number_input("Quantity", min_value=1, step=1)
        purchase_price = st.number_input("Purchase Price", min_value=0.0, step=1.0)
        current_value = st.number_input("Current Market Value", min_value=0.0, step=1.0)

        submitted = st.form_submit_button("Add Card")

        if submitted:
            add_card(
                name,
                game,
                set_name,
                card_number,
                condition,
                quantity,
                purchase_price,
                current_value
            )
            st.success(f"{name} added to inventory.")

    st.divider()

    st.subheader("Current Inventory")

    cards = get_all_cards()

    if cards:
        inventory_data = []

        for card in cards:
            card_id, name, game, set_name, card_number, condition, quantity, purchase_price, current_value = card

            total_cost = quantity * purchase_price
            total_value = quantity * current_value
            profit_loss = total_value - total_cost

            inventory_data.append({
                "ID": card_id,
                "Name": name,
                "Game": game,
                "Set": set_name,
                "Card Number": card_number,
                "Condition": condition,
                "Qty": quantity,
                "Paid Each": purchase_price,
                "Market Each": current_value,
                "Total Cost": total_cost,
                "Total Value": total_value,
                "Profit/Loss": profit_loss
            })

        st.dataframe(inventory_data, use_container_width=True)

        st.subheader("Delete a Card")
        card_id_to_delete = st.number_input("Enter card ID to delete", min_value=1, step=1)

        if st.button("Delete Card"):
            delete_card(card_id_to_delete)
            st.warning(f"Card ID {card_id_to_delete} deleted. Refresh the page to update the table.")

    else:
        st.info("No cards in inventory yet.")
