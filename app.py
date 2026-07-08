import streamlit as st
import pandas as pd
import plotly.express as px

from services.ebay_api import search_ebay_cards
from services.recommendations import get_recommendation
from services.scanner import identify_card_from_image
from services.card_detector import analyze_card_image
from services.exporter import create_inventory_excel
from database.database import create_cards_table, add_card, get_all_cards, delete_card

create_cards_table()

st.set_page_config(page_title="Chase Vault Market Tracker", layout="wide")

st.title("Chase Vault Market Tracker")
st.write("Track trading card values, compare eBay prices, and manage your inventory.")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Inventory", "eBay Market Search", "Card Analysis", "AI Scanner"]
)


def build_inventory_data():
    cards = get_all_cards()
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

    return inventory_data


if page == "Dashboard":
    st.header("Dashboard")
    st.write("Welcome to your trading card market tracker.")

    inventory_data = build_inventory_data()

    if inventory_data:
        df = pd.DataFrame(inventory_data)

        total_value = df["Total Value"].sum()
        total_cost = df["Total Cost"].sum()
        profit_loss = total_value - total_cost
        cards_tracked = df["Qty"].sum()

        st.metric("Portfolio Value", f"${total_value:,.2f}")
        st.metric("Total Profit/Loss", f"${profit_loss:,.2f}")
        st.metric("Cards Tracked", int(cards_tracked))

        fig = px.bar(df, x="Name", y="Profit/Loss", title="Profit/Loss by Card")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.metric("Portfolio Value", "$0.00")
        st.metric("Cards Tracked", "0")
        st.metric("Market Alerts", "0")


elif page == "Inventory":
    st.header("Card Inventory")

    st.subheader("Add a Card")

    with st.form("add_card_form"):
        name = st.text_input("Card Name")
        game = st.selectbox("Game", ["Pokemon", "One Piece", "Sports", "Magic", "Yu-Gi-Oh", "Other"])
        set_name = st.text_input("Set Name")
        card_number = st.text_input("Card Number")
        condition = st.selectbox(
            "Condition",
            ["Raw", "Near Mint", "Lightly Played", "Moderately Played", "Damaged", "Graded"]
        )
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

    inventory_data = build_inventory_data()

    if inventory_data:
        st.dataframe(inventory_data, use_container_width=True)

        excel_file = create_inventory_excel(inventory_data)

        st.download_button(
            label="Export Inventory to Excel",
            data=excel_file,
            file_name="chase_vault_inventory.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.subheader("Delete a Card")
        card_id_to_delete = st.number_input("Enter card ID to delete", min_value=1, step=1)

        if st.button("Delete Card"):
            delete_card(card_id_to_delete)
            st.warning(f"Card ID {card_id_to_delete} deleted. Refresh the page to update the table.")
    else:
        st.info("No cards in inventory yet.")


elif page == "eBay Market Search":
    st.header("eBay Market Search")
    st.write("Search eBay listings and view card images, prices, conditions, and listing links.")

    card_name = st.text_input("Enter card name")

    if st.button("Search eBay"):
        if not card_name.strip():
            st.warning("Please enter a card name before searching.")
        else:
            results = search_ebay_cards(card_name)

            st.subheader("eBay Results")

            for item in results:
                col1, col2 = st.columns([1, 3])

                with col1:
                    if item.get("image_url"):
                        st.image(
                            item["image_url"],
                            caption="Listing Image",
                            use_container_width=True
                        )
                    else:
                        st.write("No image available")

                with col2:
                    st.write(f"### {item['title']}")
                    st.write(f"**Price:** ${item['price']}")
                    st.write(f"**Condition:** {item['condition']}")

                    if item.get("item_url"):
                        st.link_button("View eBay Listing", item["item_url"])

                st.divider()

elif page == "Card Analysis":
    st.header("Card Analysis")

    card_name = st.text_input("Card Name")
    purchase_price = st.number_input("Purchase Price", min_value=0.0, step=1.0)
    current_price = st.number_input("Current Market Price", min_value=0.0, step=1.0)
    quantity = st.number_input("Quantity", min_value=1, step=1)

    if st.button("Analyze Card"):
        total_cost = purchase_price * quantity
        total_value = current_price * quantity
        profit_loss = total_value - total_cost
        recommendation = get_recommendation(purchase_price, current_price)

        st.subheader("Analysis Results")
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
        st.plotly_chart(fig, use_container_width=True)


elif page == "AI Scanner":
    st.header("AI Card Scanner")
    st.write(
        "Use your phone camera to scan a trading card. "
        "The app will check if the card is centered and clear before adding it to inventory."
    )

    camera_image = st.camera_input("Take a picture of the card")

    if camera_image is not None:
        analysis = analyze_card_image(camera_image)

        st.subheader("Card Tracking Preview")

        if analysis["annotated_image"] is not None:
            st.image(
                analysis["annotated_image"],
                caption="Detected Card Outline",
                use_container_width=True
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Center Score", f"{analysis['center_score']}%")

        with col2:
            st.metric("Sharpness", analysis["sharpness"])

        with col3:
            st.metric("Brightness", analysis["brightness"])

        if analysis["ready"]:
            st.success(analysis["message"])

            st.subheader("Auto-Cropped Card")

            if analysis["cropped_image"] is not None:
                st.image(
                    analysis["cropped_image"],
                    caption="Cropped Card for AI Identification",
                    use_container_width=True
                )

            if st.button("Use This Scan"):
                scan_result = identify_card_from_image(analysis["cropped_image"])
                st.session_state["scan_result"] = scan_result
                st.success("Card scan accepted. Review the details below before adding it to inventory.")
        else:
            st.warning(analysis["message"])
            st.info("Retake the picture after adjusting the card position, distance, lighting, or focus.")

    if "scan_result" in st.session_state:
        result = st.session_state["scan_result"]

        st.subheader("Review Scanned Card")

        with st.form("add_scanned_card_form"):
            name = st.text_input("Card Name", value=result["name"])

            game_options = ["Pokemon", "One Piece", "Sports", "Magic", "Yu-Gi-Oh", "Other"]

            game = st.selectbox(
                "Game",
                game_options,
                index=game_options.index(result["game"]) if result["game"] in game_options else 5
            )

            set_name = st.text_input("Set Name", value=result["set"])
            card_number = st.text_input("Card Number", value=result["card_number"])

            condition = st.selectbox(
                "Condition",
                ["Raw", "Near Mint", "Lightly Played", "Moderately Played", "Damaged", "Graded", "Needs Review"],
                index=6
            )

            quantity = st.number_input("Quantity", min_value=1, step=1)
            purchase_price = st.number_input("Purchase Price", min_value=0.0, step=1.0)
            current_value = st.number_input("Current Market Value", min_value=0.0, step=1.0)

            submitted = st.form_submit_button("Add Scanned Card to Inventory")

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
                del st.session_state["scan_result"]
