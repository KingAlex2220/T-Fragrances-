import streamlit as st
import sqlite3
import random
import datetime
import os
import pandas as pd

# --- PAGE SETUP & BRANDING ---
st.set_page_config(page_title="T Fragrances - Storefront & POS", page_icon="✨", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E293B; font-family: \"Segoe UI\", sans-serif; margin-bottom: 0;'>T FRAGRANCES</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #64748B; font-size: 1.1rem; margin-top: 5px;'>Designer Quality | 100% Pure Oil-Based | Reimagined Luxury</p>", unsafe_allow_html=True)
st.markdown("---")

# --- DATA STORAGE SETUP ---
DB_FILE = "t_fragrances.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders_v2 (
            order_id TEXT PRIMARY KEY,
            timestamp TEXT,
            customer_name TEXT,
            phone_number TEXT,
            delivery_address TEXT,
            category TEXT,
            product_code TEXT,
            scent_name TEXT,
            payment_method TEXT,
            total_paid REAL,
            status TEXT,
            order_type TEXT
        )
    """)
    try:
        cursor.execute("SELECT quantity FROM orders_v2 LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE orders_v2 ADD COLUMN quantity INTEGER DEFAULT 1")
    conn.commit()
    conn.close()

init_db()

# --- EMBEDDED MASTER CATALOG ---
men_catalog = [
    {"code": "#48E", "label": "#48E | Creed - Aventus", "scent": "Aventus"},
    {"code": "#135G", "label": "#135G | Paco Rabanne - Invictus", "scent": "Invictus"},
    {"code": "#91", "label": "#91 | Jimmy Choo - Man", "scent": "Man"},
    {"code": "#135A", "label": "#135A | Paco Rabanne - One Million", "scent": "One Million"},
    {"code": "#53B", "label": "#53B | Dolce & Gabbana - Light Blue", "scent": "Light Blue"},
    {"code": "#53G", "label": "#53G | Dolce & Gabbana - King", "scent": "King"},
    {"code": "#168J", "label": "#168J | YSL - Myself Absolute", "scent": "Myself Absolute"},
    {"code": "#18G", "label": "#18G | Armani - Armani Code", "scent": "Armani Code"},
    {"code": "#15A", "label": "#15A | Maison Francis Kurkdjian - Baccarat 540", "scent": "Baccarat 540"},
    {"code": "#43B", "label": "#43B | Christian Dior - Sauvage", "scent": "Sauvage"}
]

women_catalog = [
    {"code": "#15A", "label": "#15A | Baccarat - Rouge 540", "scent": "Rouge 540"},
    {"code": "#16", "label": "#16 | Chanel - Coco Mademoiselle", "scent": "Coco Mademoiselle"},
    {"code": "#17", "label": "#17 | Dior - Miss Dior", "scent": "Miss Dior"},
    {"code": "#21A", "label": "#21A | Chanel - Chance", "scent": "Chance"}
]

home_catalog = [
    {"code": "H#1", "label": "H#1 | House Blend - Laundry day", "scent": "Laundry day"},
    {"code": "H#2", "label": "H#2 | House Blend - Gain", "scent": "Gain"},
    {"code": "H#3", "label": "H#3 | House Blend - Apple Blossom", "scent": "Apple Blossom"}
]

PRICE_PER_BOTTLE = 80.00
LOCAL_BOTTLE_IMG = "images/bottles.png"
LOCAL_QR_IMG = "images/zelle_qr.png"

# --- SIDEBAR ACCESS INTERFACE ---
st.sidebar.markdown("### 🔒 System Portal")
access_mode = "🛍️ Public Storefront"

with st.sidebar.expander("Staff Portal", expanded=False):
    password = st.text_input("Enter Admin Password:", type="password", key="admin_password_input")

if password == "tf80":
    st.sidebar.success("Authenticated")
    access_mode = st.sidebar.radio("View Mode", ["🛍️ Public Storefront", "💼 Owner Dashboard"])
elif password:
    st.sidebar.error("Incorrect Password")

# ==========================================
# PUBLIC VIEW: ONLINE STOREFRONT & TRACKING
# ==========================================
if access_mode == "🛍️ Public Storefront":
    # Split the storefront into two easy sections for customers
    public_tab_shop, public_tab_track = st.tabs(["🛍️ Shop Online", "📦 Track My Order"])
    
    with public_tab_shop:
        st.subheader("🛍️ Place Your Order Online")
        col_store_left, col_store_right = st.columns([3, 2])
        
        with col_store_left:
            with st.container(border=True):
                st.markdown("#### 1. Select Your Line Segment")
                cat_select = st.radio("Product Family:", ["Men's Premium Oils", "Women's Premium Oils", "Home & House Scents"], horizontal=True)
                active_list = men_catalog if cat_select == "Men's Premium Oils" else (women_catalog if cat_select == "Women's Premium Oils" else home_catalog)
                    
                st.markdown("#### 2. Choose Your Scent & Size")
                selected_display = st.selectbox("Available Inventory Index:", [item["label"] for item in active_list])
                matching_obj = next(item for item in active_list if item["label"] == selected_display)
                
                web_qty = st.number_input("Select Quantity:", min_value=1, max_value=50, value=1, step=1, key="web_quantity_select")
                
                if os.path.exists(LOCAL_BOTTLE_IMG):
                    st.image(LOCAL_BOTTLE_IMG, caption=f"Signature Presentation Model — Featured Scent: {matching_obj['scent']}", use_container_width=True)
                else:
                    st.info("💡 Image loading configuration pending sync.")
                
                st.markdown("#### 3. Shipping & Contact Information")
                cust_name = st.text_input("Full Name:")
                cust_phone = st.text_input("Phone Number:", placeholder="+18635550199")
                cust_address = st.text_area("Full Shipping / Delivery Address:", placeholder="Street, City, State, ZIP")
                submit_order = st.button("Review Order Invoice", type="primary")
                
            if submit_order:
                if not cust_name.strip() or not cust_phone.strip() or not cust_address.strip():
                    st.error("⚠️ Please fill out your Name, Phone Number, and Shipping Address.")
                else:
                    st.session_state.web_cart = {
                        "name": cust_name.strip(),
                        "phone": cust_phone.strip(),
                        "address": cust_address.strip(),
                        "category": cat_select,
                        "code": matching_obj["code"],
                        "scent": matching_obj["scent"],
                        "quantity": int(web_qty),
                        "total": float(PRICE_PER_BOTTLE * web_qty)
                    }

        with col_store_right:
            st.markdown("#### 🧾 Order Invoice & Payment Breakdown")
            if "web_cart" in st.session_state and st.session_state.web_cart is not None:
                cart = st.session_state.web_cart
                st.info("⚙️ **Invoice Generated Successfully**")
                st.metric("Total Balance Due", f"${cart['total']:.2f}")
                st.write(f"• **Purchaser:** {cart['name']}")
                st.write(f"• **Phone:** {cart['phone']}")
                st.write(f"• **Selection:** {cart['code']} - {cart['scent']}")
                st.write(f"• **Quantity Ordered:** {cart['quantity']} bottle(s)")
                
                if st.button("Confirm & Place Order"):
                    generated_id = f"TF-WEB-{random.randint(1000, 9999)}"
                    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO orders_v2 (order_id, timestamp, customer_name, phone_number, delivery_address, category, product_code, scent_name, quantity, payment_method, total_paid, status, order_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (generated_id, timestamp_str, cart['name'], cart['phone'], cart['address'], cart['category'], cart['code'], cart['scent'], cart['quantity'], "Zelle Pending", cart['total'], "Awaiting Payment", "Online Store"))
                    conn.commit()
                    conn.close()
                    
                    send_sms_confirmation(to_phone=cart['phone'], customer_name=cart['name'], order_id=generated_id, total_amount=cart['total'])
                    
                    st.session_state.last_order_id = generated_id
                    st.session_state.last_order_total = cart['total']
                    st.session_state.web_cart = None
                    st.rerun()
                    
            elif "last_order_id" in st.session_state:
                st.success(f"🎉 Order Placed! ID: {st.session_state.last_order_id}")
                st.info("📱 A text confirmation has been sent to your phone number.")
                st.markdown("### 💰 Scan or Use Info to Pay:")
                st.markdown(f"""
                Send your **${st.session_state.get('last_order_total', PRICE_PER_BOTTLE):.2f}** payment via **Zelle**:
                * **Recipient Phone:** `863-236-4196`
                * **Name:** Alexander Thompson
                
                ⚠️ **IMPORTANT:** Include your Order ID **`{st.session_state.last_order_id}`** in the Zelle memo note!
                """)
                if os.path.exists(LOCAL_QR_IMG):
                    st.image(LOCAL_QR_IMG, caption="Scan with your banking app to Zelle instantly", width=300)
                if st.button("Clear Screen / Place New Order"):
                    if "last_order_id" in st.session_state: del st.session_state.last_order_id
                    if "last_order_total" in st.session_state: del st.session_state.last_order_total
                    st.rerun()
            else:
                st.info("Select a scent and fill out details to view invoice configurations.")

    # --- CUSTOMER FULFILLMENT TRACKING INTERFACE ---
    with public_tab_track:
        st.subheader("📦 Real-Time Order Tracking Portal")
        st.write("Enter your order tracking code (e.g., `TF-WEB-1234`) below to verify your current fulfillment status.")
        
        search_id = st.text_input("Tracking Code:", placeholder="TF-WEB-XXXX", key="customer_track_input").strip()
        
        if st.button("Check Order Status", type="primary"):
            if search_id:
                try:
                    conn = get_db_connection()
                    row = conn.execute("SELECT * FROM orders_v2 WHERE order_id = ?", (search_id,)).fetchone()
                    conn.close()
                    
                    if row:
                        st.markdown("---")
                        st.markdown(f"### Order Details for **{row['order_id']}**")
                        
                        # Set custom status badges and progress updates depending on the ledger entry
                        status_str = row["status"]
                        
                        if status_str == "Awaiting Payment":
                            st.warning("⏳ Status: **Awaiting Zelle Payment Verification**")
                            st.info("💡 Next Step: Once your Zelle payment matches our records, your order status will progress automatically to processing.")
                        elif status_str == "Paid & Processing":
                            st.info("📦 Status: **Payment Verified — Order is Packing / Processing**")
                            st.success("👍 Next Step: Your fragrance package is currently being processed by fulfillment handlers.")
                        elif status_str == "Completed & Handed Over":
                            st.success("✅ Status: **Order Complete & Fulfilled!**")
                        elif status_str == "Cancelled":
                            st.error("❌ Status: **Order Cancelled**")
                        else:
                            st.info(f"📋 Status: **{status_str}**")
                            
                        # Show visual details breakdown to reassure customer
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Items Ordered", f"{row['quantity']} Bottle(s)")
                        col2.metric("Total Paid Amount", f"${row['total_paid']:.2f}")
                        col3.write(f"**Item Description:**\n{row['product_code']} — {row['scent_name']}")
                        
                    else:
                        st.error("❌ Invalid Tracking Code. Please verify your order number and try again.")
                except Exception:
                    st.error("⚠️ System Error: Unable to query database records.")
            else:
                st.warning("Please type in an Order ID first.")

# ==========================================
# PRIVATE VIEW: OWNER HUB & POS
# ==========================================
else:
    st.subheader("💼 Master Business Operations Hub")
    tab_pos, tab_web_orders, tab_track, tab_ops = st.tabs(["🛒 In-Person POS Terminal", "📬 Pending Web Orders", "📦 Order Lookup", "🛡️ Master Database Ledger"])
    
    with tab_pos:
        st.markdown("### Hand-to-Hand Retail Register")
        col_entry, col_invoice = st.columns([3, 2])
        with col_entry:
            with st.container(border=True):
                cat_select = st.radio("In-Person Line Segment:", ["Men's Premium Oils", "Women's Premium Oils", "Home & House Scents"], horizontal=True, key="pos_cat")
                active_list = men_catalog if cat_select == "Men's Premium Oils" else (women_catalog if cat_select == "Women's Premium Oils" else home_catalog)
                selected_display = st.selectbox("Search master index:", [item["label"] for item in active_list], key="pos_scent")
                matching_obj = next(item for item in active_list if item["label"] == selected_display)
                
                pos_qty = st.number_input("In-Person Quantity:", min_value=1, max_value=100, value=1, step=1, key="pos_qty_select")
                client_name = st.text_input("Walk-in Customer Name:", placeholder="Jane Doe")
                payment_vector = st.selectbox("Settlement Channel:", ["Cash", "Zelle Scan", "Apple Pay", "Venmo", "Cash App"])
                generate_click = st.button("Process Live Checkout Configuration")
                
            if generate_click:
                if not client_name.strip():
                    st.error("Please enter a valid Customer Name.")
                else:
                    st.session_state.pos_cart = {
                        "client": client_name.strip(),
                        "category": cat_select,
                        "code": matching_obj["code"],
                        "scent": matching_obj["scent"],
                        "vector": payment_vector,
                        "quantity": int(pos_qty),
                        "price": float(PRICE_PER_BOTTLE * pos_qty)
                    }
                    
        with col_invoice:
            if "pos_cart" in st.session_state and st.session_state.pos_cart is not None:
                cart = st.session_state.pos_cart
                st.warning(f"**Awaiting Settlement Verification via {cart['vector']}**")
                st.metric("Immediate Cash Flow Collected", f"${cart['price']:.2f}")
                st.write(f"• **Customer:** {cart['client']}")
                st.write(f"• **Scent:** {cart['scent']} ({cart['quantity']} Unit(s))")
                
                if st.button("Commit Sale to Ledger"):
                    generated_id = f"TF-POS-{random.randint(1000, 9999)}"
                    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO orders_v2 (order_id, timestamp, customer_name, phone_number, delivery_address, category, product_code, scent_name, quantity, payment_method, total_paid, status, order_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (generated_id, timestamp_str, cart['client'], 'N/A', 'In-Person Sale', cart['category'], cart['code'], cart['scent'], cart['quantity'], cart['vector'], cart['price'], "Completed & Handed Over", "POS Register"))
                    conn.commit()
                    conn.close()
                    st.success(f"Transaction Recorded! Code: {generated_id}")
                    st.balloons()
                    st.session_state.pos_cart = None
            else:
                st.info("POS Terminal completely clear and ready.")

    with tab_web_orders:
        st.markdown("### Online Orders Awaiting Verification")
        try:
            conn = get_db_connection()
            pending_df = pd.read_sql_query("SELECT order_id, timestamp, customer_name, phone_number, product_code, scent_name, quantity, total_paid, status FROM orders_v2 WHERE order_type = 'Online Store' AND (status = 'Awaiting Payment' OR status = 'Paid & Processing')", conn)
            conn.close()
            if pending_df.empty:
                st.success("No pending web orders require attention.")
            else:
                st.dataframe(pending_df, use_container_width=True)
                target_order = st.selectbox("Select Order ID to update:", pending_df["order_id"].tolist())
                next_action = st.radio("Action:", ["Mark as Paid & Ready to Pack/Ship", "Mark as Completed / Handed Over", "Cancel / Payment Rejected"])
                if st.button("Execute Action State Update"):
                    if "Mark as Paid" in next_action:
                        new_status = "Paid & Processing"
                    elif "Mark as Completed" in next_action:
                        new_status = "Completed & Handed Over"
                    else:
                        new_status = "Cancelled"
                        
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE orders_v2 SET status = ? WHERE order_id = ?", (new_status, target_order))
                    conn.commit()
                    conn.close()
                    st.success(f"Order {target_order} updated to: {new_status}")
                    st.rerun()
        except Exception:
            st.info("No active web orders in logging memory.")

    with tab_track:
        st.markdown("### System Pipeline Diagnostic Registry")
        user_query_input = st.text_input("Input Target Tracking Order Code:", placeholder="TF-WEB-1234", key="owner_lookup_field").strip()
        if st.button("Query Database", key="owner_lookup_btn"):
            if user_query_input:
                try:
                    conn = get_db_connection()
                    row = conn.execute("SELECT * FROM orders_v2 WHERE order_id = ?", (user_query_input,)).fetchone()
                    conn.close()
                    if row:
                        st.markdown(f"### Update Diagnostic: Order Found ✅")
                        st.metric("Fulfillment Processing Status", row["status"])
                        st.write(f"• **Quantity:** {row['quantity']} Unit(s) — **Total:** ${row['total_paid']:.2f}")
                    else:
                        st.error("No transaction found.")
                except Exception:
                    st.error("Database error.")

    with tab_ops:
        st.markdown("### Complete Global Financial Ledger Matrix")
        try:
            conn = get_db_connection()
            df_orders = pd.read_sql_query("SELECT * FROM orders_v2 ORDER BY timestamp DESC", conn)
            conn.close()
            if not df_orders.empty:
                st.dataframe(df_orders, use_container_width=True)
            else:
                st.info("The business database log is empty.")
        except Exception:
            st.info("The business database log is empty.")
