import streamlit as st
import sqlite3
import time
from datetime import datetime

# Database Connection Helper
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Main App Layout
st.set_page_config(page_title="T-Fragrances", page_icon="✨", layout="wide")
st.title("✨ T-Fragrances Order Portal")

# Setup Tabs
order_tab, track_tab = st.tabs(["🛒 Place Order", "📦 Track Order"])

with order_tab:
    st.header("Order & Preorder")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Customer Details")
        cust_name = st.text_input("Full Name")
        cust_phone = st.text_input("Phone Number")
        cust_addr = st.text_input("Delivery Address")

        st.subheader("Product Selection")
        cat_select = st.selectbox("Category", ["Fragrance Oils", "Perfumes", "Body Care"])
        
        # Sample products - replace/expand as needed
        products = {
            "Fragrance Oils": ["Vanilla Musk", "Amber Nights", "Sandalwood Rose"],
            "Perfumes": ["Velvet Noir", "Ocean Breeze", "Citrus Glow"],
            "Body Care": ["Shea Butter Lotion", "Exfoliating Scrub"]
        }
        
        matching_obj = st.selectbox("Select Scent", products.get(cat_select, []))
        web_qty = st.number_input("Quantity", min_value=1, value=1)
        
        # Sample pricing logic
        unit_price = 25.0
        final_total = unit_price * web_qty
        
        payment_method = st.selectbox("Payment / Settlement Channel:", ["Zelle", "CashApp", "Apple Pay", "Cash on Delivery"])
        is_preorder_val = st.checkbox("Mark as Priority Preorder")

        if st.button("Generate Invoice / Add to Cart", type="primary"):
            if not cust_name or not cust_phone:
                st.error("Please enter your Name and Phone Number.")
            else:
                st.session_state.web_cart = {
                    "name": cust_name.strip(),
                    "phone": cust_phone.strip(),
                    "address": cust_addr.strip(),
                    "category": cat_select,
                    "code": matching_obj,
                    "scent": matching_obj,
                    "quantity": int(web_qty),
                    "total": float(final_total),
                    "payment_method": payment_method,
                    "is_preorder": 1 if is_preorder_val else 0
                }
                st.success("Invoice generated! Review on the right side.")

    with col2:
        st.subheader("Order Summary & Invoice")

        if "web_cart" in st.session_state:
            cart = st.session_state.web_cart
            st.info("⚙️ **Invoice Generated Successfully**")

            if cart.get("is_preorder", 0) == 1:
                st.warning("⭐ **PRIORITY PREORDER ORDER**")

            st.metric("Total Balance", f"${cart['total']:.2f}")
            st.write(f"• **Purchaser:** {cart['name']}")
            st.write(f"• **Phone:** {cart['phone']}")
            st.write(f"• **Selection:** {cart['category']} - {cart['scent']}")
            st.write(f"• **Quantity:** {cart['quantity']}")
            st.write(f"• **Settlement:** {cart['payment_method']}")
            st.write(f"• **Order Type:** {'Preorder' if cart['is_preorder'] else 'Standard'}")

            confirm_label = "Confirm & Place Priority Preorder" if cart['is_preorder'] else "Confirm Order"
            
            if st.button(confirm_label, type="primary"):
                generated_id = f"TF-{int(time.time())}"
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                initial_status = "Preorder Pending" if cart['is_preorder'] else "Pending"

                # Record Order in DB
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Ensure table exists
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS orders (
                            order_id TEXT PRIMARY KEY,
                            timestamp TEXT,
                            name TEXT,
                            phone TEXT,
                            address TEXT,
                            category TEXT,
                            scent TEXT,
                            quantity INTEGER,
                            total REAL,
                            status TEXT
                        )
                    """)

                    cursor.execute(
                        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (generated_id, timestamp_str, cart['name'], cart['phone'], cart['address'], cart['category'], cart['scent'], cart['quantity'], cart['total'], initial_status)
                    )
                    conn.commit()
                    conn.close()

                    if cart.get("is_preorder", 0) == 0:
                        st.success(f"🎉 **Order Placed! ID:** `{generated_id}`")
                    else:
                        st.success(f"🚀 **Preorder Placed! ID:** `{generated_id}`")

                    st.session_state.last_order_id = generated_id
                    st.session_state.last_order_total = cart['total']
                    st.session_state.last_order_method = cart['payment_method']
                    st.session_state.last_order_preorder = cart.get("is_preorder", 0)
                    st.session_state.pop("web_cart", None)
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to record order: {e}")

            st.divider()
            if st.button("Place New Order / Clear Cart"):
                for key in ["web_cart", "last_order_id", "last_order_total", "last_order_method", "last_order_preorder"]:
                    st.session_state.pop(key, None)
                st.rerun()

        else:
            st.info("Select a scent to generate an order preview.")

with track_tab:
    st.subheader("📦 Real-Time Order Tracking")
    st.write("Enter your **Order ID** or **Phone Number** below:")

    cust_query_input = st.text_input("Search Order:")

    if st.button("Track Order", type="primary"):
        if cust_query_input:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                clean_input = cust_query_input.strip()
                
                query = """
                    SELECT * FROM orders 
                    WHERE order_id = ? 
                    OR phone = ?
                    ORDER BY timestamp DESC
                """
                rows = cursor.execute(query, (clean_input, clean_input)).fetchall()
                conn.close()

                if rows:
                    st.markdown("---")
                    for row in rows:
                        st.markdown(f"### Order ID: `{row['order_id']}`")
                        st.write(f"• **Date:** {row['timestamp']}")
                        st.write(f"• **Item:** {row['category']} - {row['scent']} (x{row['quantity']})")
                        st.write(f"• **Total:** ${row['total']:.2f}")
                        st.write(f"• **Status:** `{row['status']}`")
                        st.markdown("---")
                else:
                    st.warning("No orders found matching that Order ID or Phone Number.")
            except Exception as e:
                st.error(f"Error querying database: {e}")
        else:
            st.error("Please enter an Order ID or Phone Number.")
