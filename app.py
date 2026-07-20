import streamlit as st
import sqlite3
import random
import datetime
import os
import pandas as pd

# --- PAGE SETUP & BRANDING ---
st.set_page_config(page_title="T Fragrances - Storefront & POS", page_icon="✨", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E293B; font-family: \"Segoe UI\", sans-serif; margin-bottom: 0;'>T FRAGRANCES</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #64748B; font-size: 1.1rem; margin-top: 5px;'>Designer Quality (30ml) | 100% Pure Oil-Based | Reimagined Luxury</p>", unsafe_allow_html=True)
st.markdown("---")

# --- DATA STORAGE SETUP ---
DB_FILE = "t_fragrances.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- EMBEDDED MASTER CATALOG ---
men_catalog = [
    {"code": "#48E", "label": "#48E | Impression of Creed - Aventus", "scent": "Impression of Aventus", "category": "Men's Premium Oils"},
    {"code": "#135G", "label": "#135G | Impression of Paco Rabanne - Invictus", "scent": "Impression of Invictus", "category": "Men's Premium Oils"},
    {"code": "#91", "label": "#91 | Impression of Jimmy Choo - Man", "scent": "Impression of Man", "category": "Men's Premium Oils"},
    {"code": "#135A", "label": "#135A | Impression of Paco Rabanne - One Million", "scent": "Impression of One Million", "category": "Men's Premium Oils"},
    {"code": "#53B", "label": "#53B | Impression of Dolce & Gabbana - Light Blue", "scent": "Impression of Light Blue", "category": "Men's Premium Oils"},
    {"code": "#53G", "label": "#53G | Impression of Dolce & Gabbana - King", "scent": "Impression of King", "category": "Men's Premium Oils"},
    {"code": "#168J", "label": "#168J | Impression of YSL - Myself Absolute", "scent": "Impression of Myself Absolute", "category": "Men's Premium Oils"},
    {"code": "#18G", "label": "#18G | Impression of Armani - Armani Code", "scent": "Impression of Armani Code", "category": "Men's Premium Oils"},
    {"code": "#15A", "label": "#15A | Impression of Maison Francis Kurkdjian - Baccarat 540", "scent": "Impression of Baccarat 540", "category": "Men's Premium Oils"},
    {"code": "#43B", "label": "#43B | Impression of Christian Dior - Sauvage", "scent": "Impression of Sauvage", "category": "Men's Premium Oils"}
]

women_catalog = [
    {"code": "#15A", "label": "#15A | Impression of Baccarat - Rouge 540", "scent": "Impression of Rouge 540", "category": "Women's Premium Oils"},
    {"code": "#16", "label": "#16 | Impression of Chanel - Coco Mademoiselle", "scent": "Impression of Coco Mademoiselle", "category": "Women's Premium Oils"},
    {"code": "#17", "label": "#17 | Impression of Dior - Miss Dior", "scent": "Impression of Miss Dior", "category": "Women's Premium Oils"},
    {"code": "#21A", "label": "#21A | Impression of Chanel - Chance", "scent": "Impression of Chance", "category": "Women's Premium Oils"}
]

home_catalog = [
    {"code": "H#1", "label": "H#1 | House Blend - Laundry day", "scent": "Laundry day", "category": "Home & House Scents"},
    {"code": "H#2", "label": "H#2 | House Blend - Sunrise", "scent": "Sunrise", "category": "Home & House Scents"},
]

ALL_CATALOG_ITEMS = men_catalog + women_catalog + home_catalog

DEFAULT_INITIAL_STOCK = 20  # Baseline stock capacity for 100% calculation

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Base schema matching initial logic
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
    
    # Dynamic schema migrations
    try:
        cursor.execute("SELECT quantity FROM orders_v2 LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE orders_v2 ADD COLUMN quantity INTEGER DEFAULT 1")

    try:
        cursor.execute("SELECT is_preorder FROM orders_v2 LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE orders_v2 ADD COLUMN is_preorder INTEGER DEFAULT 0")

    # Inventory Table Creation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_code TEXT PRIMARY KEY,
            category TEXT,
            scent_name TEXT,
            stock_quantity INTEGER DEFAULT 20,
            initial_capacity INTEGER DEFAULT 20
        )
    """)
    
    # Populate inventory defaults if empty
    for item in ALL_CATALOG_ITEMS:
        cursor.execute("""
            INSERT OR IGNORE INTO inventory (product_code, category, scent_name, stock_quantity, initial_capacity)
            VALUES (?, ?, ?, ?, ?)
        """, (item["code"], item["category"], item["scent"], DEFAULT_INITIAL_STOCK, DEFAULT_INITIAL_STOCK))
        
    conn.commit()
    conn.close()

init_db()

# --- HELPER INVENTORY FUNCTIONS ---
def get_item_stock(product_code):
    conn = get_db_connection()
    row = conn.execute("SELECT stock_quantity, initial_capacity FROM inventory WHERE product_code = ?", (product_code,)).fetchone()
    conn.close()
    if row:
        return row["stock_quantity"], row["initial_capacity"]
    return DEFAULT_INITIAL_STOCK, DEFAULT_INITIAL_STOCK

def deduct_inventory(product_code, qty):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE inventory SET stock_quantity = MAX(0, stock_quantity - ?) WHERE product_code = ?", (qty, product_code))
    conn.commit()
    conn.close()

def restock_item(product_code, add_qty):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE inventory SET stock_quantity = stock_quantity + ? WHERE product_code = ?", (add_qty, product_code))
    conn.commit()
    conn.close()

PRICE_PER_BOTTLE = 80.00
LOCAL_BOTTLE_IMG = "images/bottles.png"
LOCAL_QR_IMG = "images/zelle_qr.png"

# --- SIDEBAR ACCESS INTERFACE (SECURED & HIDDEN BY DEFAULT) ---
st.sidebar.markdown("### 🔒 System Portal")

# Default view for regular users
access_mode = "🛍️ Public Storefront"

# Expanded is explicitly forced to False to keep the menu collapsed on load
with st.sidebar.expander("Staff Portal", expanded=False):
    password = st.text_input("Enter Admin Password:", type="password", key="admin_password_input")

# Only grant visibility to the Dashboard if password matches 'Safe9uard-tf80'
if password == "Safe9uard-tf80":
    st.sidebar.success("Authenticated")
    access_mode = st.sidebar.radio("View Mode", ["🛍️ Public Storefront", "💼 Owner Dashboard"])
elif password:
    st.sidebar.error("Incorrect Password")

# ==========================================
# PUBLIC VIEW: ONLINE STOREFRONT
# ==========================================
if access_mode == "🛍️ Public Storefront":
    store_tab, track_tab = st.tabs(["🛍️ Order Online", "📦 Track My Order"])
    
    with store_tab:
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
                
                # Check current stock level
                current_stock, initial_cap = get_item_stock(matching_obj["code"])
                is_preorder_item = current_stock <= 0
                
                if is_preorder_item:
                    st.info("⭐ **PRIORITY PREORDER ITEM:** Regular stock is currently reserved/sold out. Placing a order reserves your bottle in our upcoming priority batch!")
                elif current_stock <= (initial_cap * 0.5):
                    st.warning(f"⚠️ Limited Regular Stock Remaining! (Only {current_stock} left)")
                else:
                    st.caption(f"In Stock ({current_stock} available)")

                # Quantity selection
                max_selectable = 50 if is_preorder_item else max(1, current_stock)
                web_qty = st.number_input("Select Quantity:", min_value=1, max_value=max_selectable, value=1, step=1, key="web_quantity_select")
                
                if os.path.exists(LOCAL_BOTTLE_IMG):
                    st.image(LOCAL_BOTTLE_IMG, caption=f"Signature Presentation Model — Featured Scent: {matching_obj['scent']}", use_container_width=True)
                else:
                    st.info("💡 Image loading configuration pending sync.")
                
                st.markdown("#### 3. Shipping & Contact Information")
                cust_name = st.text_input("Full Name:")
                cust_phone = st.text_input("Phone Number:")
                cust_address = st.text_area("Full Shipping / Delivery Address:", placeholder="Street, City, State, ZIP")
                
                st.markdown("#### 4. Select Settlement Channel")
                payment_method = st.selectbox(
                    "Payment / Settlement Channel:",
                    ["Zelle", "Cash App", "Venmo", "Apple Pay / Text Payment"],
                    help="Choose your preferred payment method to view settlement details."
                )
                
                button_label = "Review Priority Preorder Invoice" if is_preorder_item else "Review Order Invoice"
                submit_order = st.button(button_label, type="primary")
                
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
                        "total": float(PRICE_PER_BOTTLE * web_qty),
                        "payment_method": payment_method,
                        "is_preorder": 1 if is_preorder_item else 0
                    }

        with col_store_right:
            st.markdown("#### 🧾 Order Invoice & Payment Breakdown")
            if "web_cart" in st.session_state and st.session_state.web_cart is not None:
                cart = st.session_state.web_cart
                st.info("⚙️ **Invoice Generated Successfully**")
                
                if cart.get("is_preorder", 0) == 1:
                    st.warning("⭐ **PRIORITY PREORDER STATUS APPLIED**")
                    
                st.metric("Total Balance Due", f"${cart['total']:.2f}")
                st.write(f"• **Purchaser:** {cart['name']}")
                st.write(f"• **Phone:** {cart['phone']}")
                st.write(f"• **Selection:** {cart['code']} - {cart['scent']}")
                st.write(f"• **Quantity Ordered:** {cart['quantity']} bottle(s)")
                st.write(f"• **Settlement Channel:** {cart['payment_method']}")
                st.write(f"• **Order Type:** {'Priority Preorder' if cart.get('is_preorder') == 1 else 'Standard In-Stock'}")
                
                confirm_label = "Confirm & Place Priority Preorder" if cart.get("is_preorder") == 1 else "Confirm & Place Order"
                if st.button(confirm_label):
                    generated_id = f"TF-WEB-{random.randint(1000, 9999)}"
                    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    initial_status = "Preorder - Awaiting Batch Restock" if cart.get("is_preorder", 0) == 1 else f"Awaiting Payment ({cart['payment_method']})"
                    
                    # Record Order in DB
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO orders_v2 (order_id, timestamp, customer_name, phone_number, delivery_address, category, product_code, scent_name, quantity, payment_method, total_paid, status, order_type, is_preorder)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (generated_id, timestamp_str, cart['name'], cart['phone'], cart['address'], cart['category'], cart['code'], cart['scent'], cart['quantity'], cart['payment_method'], cart['total'], initial_status, "Online Store", cart.get("is_preorder", 0)))
                    conn.commit()
                    conn.close()
                    
                    # Deduct from stock if regular stock
                    if cart.get("is_preorder", 0) == 0:
                        deduct_inventory(cart['code'], cart['quantity'])
                    
                    st.session_state.last_order_id = generated_id
                    st.session_state.last_order_total = cart['total']
                    st.session_state.last_order_method = cart['payment_method']
                    st.session_state.last_order_preorder = cart.get("is_preorder", 0)
                    st.session_state.web_cart = None
                    st.rerun()
                    
            elif "last_order_id" in st.session_state:
                if st.session_state.get("last_order_preorder", 0) == 1:
                    st.success(f"⭐ Priority Preorder Reserved! ID: {st.session_state.last_order_id}")
                else:
                    st.success(f"🎉 Order Placed! ID: {st.session_state.last_order_id}")
                    
                selected_method = st.session_state.get('last_order_method', 'Zelle')
                order_total = st.session_state.get('last_order_total', PRICE_PER_BOTTLE)
                order_id = st.session_state.last_order_id
                
                st.markdown(f"### 💰 Send Payment via **{selected_method}**:")
                
                if selected_method == "Zelle":
                    st.markdown(f"""
                    Send **${order_total:.2f}** via **Zelle**:
                    * **Recipient Phone:** `863-236-4196`
                    * **Name:** Alexander Thompson
                    """)
                    if os.path.exists(LOCAL_QR_IMG):
                        st.image(LOCAL_QR_IMG, caption="Scan with your banking app to Zelle instantly.", width=300)
                elif selected_method == "Cash App":
                    st.markdown(f"""
                    Send **${order_total:.2f}** via **Cash App**:
                    * **Cash Tag:** `$TFragrances`
                    * **Phone:** `863-236-4196`
                    """)
                elif selected_method == "Venmo":
                    st.markdown(f"""
                    Send **${order_total:.2f}** via **Venmo**:
                    * **Username:** `@TFragrances`
                    * **Phone Verification (Last 4):** `4196`
                    """)
                else:  # Apple Pay / Text
                    st.markdown(f"""
                    Send **${order_total:.2f}** via **Apple Pay**:
                    * **Send to Phone:** `863-236-4196`
                    * **Note / Message:** Include your Order ID `{order_id}` in the text!
                    """)
                
                st.warning(f"⚠️ **IMPORTANT:** Always include your Order ID **`{order_id}`** in the payment note/memo!")
                st.caption("Please screenshot/save this tracking page for your records.")
                
                if st.button("Place New Order"):
                    if "last_order_id" in st.session_state: del st.session_state.last_order_id
                    if "last_order_total" in st.session_state: del st.session_state.last_order_total
                    if "last_order_method" in st.session_state: del st.session_state.last_order_method
                    if "last_order_preorder" in st.session_state: del st.session_state.last_order_preorder
                    st.rerun()
            else:
                st.info("Select a scent and fill out details to view invoice configurations.")

    with track_tab:
        st.subheader("📦 Real-Time Order Tracking")
        st.write("Enter your **Order ID** (e.g., `TF-WEB-1234`) or **Phone Number** to check your order status.")
        
        cust_query_input = st.text_input("Order ID or Phone Number:", placeholder="TF-WEB-1234 or 863-555-0199", key="customer_track_input").strip()
        
        if st.button("Track Order", type="primary"):
            if cust_query_input:
                try:
                    conn = get_db_connection()
                    
                    # Search by exact Order ID OR matching Phone Number
                    clean_input = cust_query_input.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                    query = """
                        SELECT * FROM orders_v2 
                        WHERE order_id = ? 
                        OR phone_number = ?
                        OR REPLACE(REPLACE(REPLACE(REPLACE(phone_number, '-', ''), ' ', ''), '(', ''), ')', '') LIKE ?
                        ORDER BY timestamp DESC
                    """
                    rows = conn.execute(query, (cust_query_input, cust_query_input, f"%{clean_input}%")).fetchall()
                    conn.close()
                    
                    if rows:
                        st.markdown("---")
                        st.markdown(f"### Found {len(rows)} Matching Order(s)")
                        
                        for row in rows:
                            with st.container(border=True):
                                status_raw = row["status"]
                                status_emoji = "⏳"
                                status_color = "orange"
                                
                                if "Preorder" in status_raw:
                                    status_emoji = "⭐"
                                    status_color = "blue"
                                elif "Paid" in status_raw or "Processing" in status_raw:
                                    status_emoji = "📦"
                                    status_color = "blue"
                                elif "Handed Over" in status_raw or "Completed" in status_raw or "Shipped" in status_raw:
                                    status_emoji = "✅"
                                    status_color = "green"
                                elif "Cancel" in status_raw:
                                    status_emoji = "❌"
                                    status_color = "red"
                                    
                                st.markdown(f"### Order ID: `{row['order_id']}`")
                                st.markdown(f"#### Status: :{status_color}[{status_emoji} {status_raw}]")
                                
                                col_details_1, col_details_2 = st.columns(2)
                                with col_details_1:
                                    st.write(f"• **Customer:** {row['customer_name']}")
                                    st.write(f"• **Phone:** {row['phone_number']}")
                                    st.write(f"• **Order Date:** {row['timestamp']}")
                                with col_details_2:
                                    st.write(f"• **Scent:** {row['scent_name']} ({row['quantity']} bottle(s))")
                                    st.write(f"• **Settlement Channel:** {row['payment_method']}")
                                    st.write(f"• **Total Value:** ${row['total_paid']:.2f}")
                                    
                                    # Safely check if is_preorder column exists in keys
                                    if "is_preorder" in row.keys() and row["is_preorder"] == 1:
                                        st.info("⭐ Prioritized Preorder Status Confirmed")
                    else:
                        st.error("No orders found matching that Order ID or Phone Number. Please check your spelling and try again.")
                except Exception as e:
                    st.error(f"An error occurred while connecting to the verification system: {e}")
            else:
                st.warning("Please type in an Order ID or Phone Number first.")

# ==========================================
# PRIVATE VIEW: OWNER HUB & POS
# ==========================================
else:
    st.subheader("💼 Master Business Operations Hub")
    
    # --- AUTOMATED SYSTEM LOW-STOCK & PREORDER ALERTS ---
    conn = get_db_connection()
    low_stock_df = pd.read_sql_query("SELECT product_code, category, scent_name, stock_quantity, initial_capacity FROM inventory WHERE stock_quantity <= (initial_capacity * 0.5)", conn)
    preorder_count_df = pd.read_sql_query("SELECT COUNT(*) as count FROM orders_v2 WHERE is_preorder = 1 AND status LIKE '%Preorder%'", conn)
    conn.close()

    pending_preorders_count = preorder_count_df.iloc[0]["count"] if not preorder_count_df.empty else 0

    if pending_preorders_count > 0:
        st.info(f"⭐ **HIGH PRIORITY ACTION:** You have **{pending_preorders_count} pending Preorder(s)** waiting for batch fulfillment!")

    if not low_stock_df.empty:
        st.warning("⚠️ **AUTOMATED INVENTORY ALERT: LOW STOCK DETECTED!**")
        for idx, row in low_stock_df.iterrows():
            if row["stock_quantity"] == 0:
                st.error(f"🚨 **{row['product_code']} - {row['scent_name']}** ({row['category']}): **OUT OF STOCK** — Currently operating in Priority Preorder mode.")
            else:
                pct = int((row["stock_quantity"] / row["initial_capacity"]) * 100)
                st.write(f"⚠️ **{row['product_code']} - {row['scent_name']}** ({row['category']}): **{row['stock_quantity']} units left** ({pct}% of capacity)")
        st.markdown("---")

    tab_preorders, tab_pos, tab_inventory, tab_web_orders, tab_track, tab_ops = st.tabs([
        "⭐ Priority Preorders Queue",
        "🛒 In-Person POS Terminal", 
        "📦 Inventory Tracker", 
        "📬 Pending Web Orders", 
        "📦 Order Lookup", 
        "🛡️ Master Database Ledger"
    ])
    
    # --- TAB: PRIORITY PREORDERS QUEUE ---
    with tab_preorders:
        st.markdown("### ⭐ Priority Preorder Fulfillment Queue")
        st.caption("Preorders take top priority. Fulfill these first as fresh batches are restocked.")
        
        conn = get_db_connection()
        preorders_df = pd.read_sql_query("SELECT order_id, timestamp, customer_name, phone_number, delivery_address, product_code, scent_name, quantity, payment_method, total_paid, status FROM orders_v2 WHERE is_preorder = 1 ORDER BY timestamp ASC", conn)
        conn.close()
        
        if preorders_df.empty:
            st.success("🎉 No pending preorders in queue! All preorders are currently fulfilled.")
        else:
            st.dataframe(preorders_df, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### ⚡ Priority Batch Fulfillment Action")
            col_p1, col_p2 = st.columns([2, 1])
            with col_p1:
                target_preorder = st.selectbox("Select Priority Preorder ID to Process:", preorders_df["order_id"].tolist())
            with col_p2:
                preorder_action = st.radio("Preorder Status Update:", ["Mark as Batch Restocked & Processing", "Mark as Shipped / Completed", "Cancel Preorder"])
                
            if st.button("Update Preorder Priority Status"):
                if "Processing" in preorder_action:
                    new_p_status = "Paid & Processing (Preorder Allocated)"
                elif "Completed" in preorder_action:
                    new_p_status = "Completed & Shipped (Preorder)"
                else:
                    new_p_status = "Cancelled Preorder"
                    
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE orders_v2 SET status = ? WHERE order_id = ?", (new_p_status, target_preorder))
                conn.commit()
                conn.close()
                st.success(f"Priority Preorder {target_preorder} updated to '{new_p_status}'!")
                st.rerun()

    with tab_pos:
        st.markdown("### Hand-to-Hand Retail Register")
        col_entry, col_invoice = st.columns([3, 2])
        with col_entry:
            with st.container(border=True):
                cat_select = st.radio("In-Person Line Segment:", ["Men's Premium Oils", "Women's Premium Oils", "Home & House Scents"], horizontal=True, key="pos_cat")
                active_list = men_catalog if cat_select == "Men's Premium Oils" else (women_catalog if cat_select == "Women's Premium Oils" else home_catalog)
                selected_display = st.selectbox("Search master index:", [item["label"] for item in active_list], key="pos_scent")
                matching_obj = next(item for item in active_list if item["label"] == selected_display)
                
                current_stock, initial_cap = get_item_stock(matching_obj["code"])
                is_pos_preorder = current_stock <= 0
                
                if is_pos_preorder:
                    st.info("⭐ **PREORDER MODE:** Regular stock is out. Processing as a Priority Preorder.")
                elif current_stock <= (initial_cap * 0.5):
                    st.warning(f"⚠️ Low Stock Alert: Only {current_stock} left")

                max_pos = 100 if is_pos_preorder else max(1, current_stock)
                pos_qty = st.number_input("In-Person Quantity:", min_value=1, max_value=max_pos, value=1, step=1, key="pos_qty_select")
                
                client_name = st.text_input("Walk-in Customer Name:", placeholder="Jane Doe")
                client_phone = st.text_input("Walk-in Customer Phone Number:", placeholder="863-555-0199")
                payment_vector = st.selectbox("Settlement Channel:", ["Cash", "Zelle", "Cash App", "Venmo", "Apple Pay"])
                generate_click = st.button("Process Live Checkout Configuration")
                
            if generate_click:
                if not client_name.strip():
                    st.error("Please enter a valid Customer Name.")
                else:
                    st.session_state.pos_cart = {
                        "client": client_name.strip(),
                        "phone": client_phone.strip() if client_phone.strip() else "N/A",
                        "category": cat_select,
                        "code": matching_obj["code"],
                        "scent": matching_obj["scent"],
                        "vector": payment_vector,
                        "quantity": int(pos_qty),
                        "price": float(PRICE_PER_BOTTLE * pos_qty),
                        "is_preorder": 1 if is_pos_preorder else 0
                    }
                    
        with col_invoice:
            if "pos_cart" in st.session_state and st.session_state.pos_cart is not None:
                cart = st.session_state.pos_cart
                st.warning(f"**Awaiting Settlement Verification via {cart['vector']}**")
                if cart.get("is_preorder") == 1:
                    st.info("⭐ Recorded as Priority Preorder")
                st.metric("Immediate Cash Flow Collected", f"${cart['price']:.2f}")
                st.write(f"• **Customer:** {cart['client']}")
                st.write(f"• **Phone:** {cart['phone']}")
                st.write(f"• **Scent:** {cart['scent']} ({cart['quantity']} Unit(s))")
                
                if st.button("Commit Sale to Ledger"):
                    generated_id = f"TF-POS-{random.randint(1000, 9999)}"
                    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    pos_status = "Preorder Recorded (In-Person)" if cart.get("is_preorder") == 1 else "Completed & Handed Over"
                    
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO orders_v2 (order_id, timestamp, customer_name, phone_number, delivery_address, category, product_code, scent_name, quantity, payment_method, total_paid, status, order_type, is_preorder)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (generated_id, timestamp_str, cart['client'], cart['phone'], 'In-Person Sale', cart['category'], cart['code'], cart['scent'], cart['quantity'], cart['vector'], cart['price'], pos_status, "POS Register", cart.get("is_preorder", 0)))
                    conn.commit()
                    conn.close()
                    
                    if cart.get("is_preorder") == 0:
                        deduct_inventory(cart['code'], cart['quantity'])
                    
                    st.success(f"Transaction Recorded! Code: {generated_id}")
                    st.balloons()
                    st.session_state.pos_cart = None
                    st.rerun()
            else:
                st.info("POS Terminal completely clear and ready.")

    # --- TAB: REAL-TIME INVENTORY TRACKER & RESTOCK PORTAL ---
    with tab_inventory:
        st.markdown("### 📦 Inventory Stock Levels & Restock Portal")
        conn = get_db_connection()
        inv_df = pd.read_sql_query("SELECT product_code AS Code, category AS Category, scent_name AS Scent, stock_quantity AS 'Stock Left', initial_capacity AS Capacity FROM inventory", conn)
        conn.close()
        
        inv_df["Stock Level (%)"] = (inv_df["Stock Left"] / inv_df["Capacity"] * 100).round(1).astype(str) + "%"
        
        st.dataframe(inv_df, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 🔄 Inventory Restock Tool")
        st.caption("📌 **Reminder:** Check the ⭐ Priority Preorders Queue to allocate new batch stock to preorders first!")
        col_r1, col_r2, col_r3 = st.columns([2, 1, 1])
        with col_r1:
            item_to_restock = st.selectbox("Select Scent to Restock:", [f"{item['code']} - {item['scent']}" for item in ALL_CATALOG_ITEMS])
        with col_r2:
            add_amount = st.number_input("Quantity to Add:", min_value=1, max_value=500, value=10, step=1)
        with col_r3:
            st.write(" ")
            st.write(" ")
            if st.button("Update Stock"):
                target_code = item_to_restock.split(" - ")[0]
                restock_item(target_code, int(add_amount))
                st.success(f"Added {add_amount} units to {target_code}!")
                st.rerun()

    with tab_web_orders:
        st.markdown("### Online Orders Awaiting Verification")
        try:
            conn = get_db_connection()
            pending_df = pd.read_sql_query("SELECT order_id, timestamp, customer_name, phone_number, product_code, scent_name, quantity, payment_method, total_paid, status, is_preorder FROM orders_v2 WHERE order_type = 'Online Store' AND (status LIKE 'Awaiting Payment%' OR status LIKE '%Preorder%')", conn)
            conn.close()
            if pending_df.empty:
                st.success("No pending web orders require attention.")
            else:
                st.dataframe(pending_df, use_container_width=True)
                target_order = st.selectbox("Select Order ID to update:", pending_df["order_id"].tolist())
                next_action = st.radio("Action:", ["Mark as Paid & Ready to Pack/Ship", "Convert to Priority Preorder Queue", "Cancel / Payment Rejected"])
                if st.button("Execute Action State Update"):
                    if "Mark as Paid" in next_action:
                        new_status = "Paid & Processing"
                    elif "Convert" in next_action:
                        new_status = "Preorder - Awaiting Batch Restock"
                    else:
                        new_status = "Cancelled"
                        
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    is_p_val = 1 if "Preorder" in new_status else 0
                    cursor.execute("UPDATE orders_v2 SET status = ?, is_preorder = ? WHERE order_id = ?", (new_status, is_p_val, target_order))
                    conn.commit()
                    conn.close()
                    st.success(f"Order {target_order} updated!")
                    st.rerun()
        except Exception:
            st.info("No active web orders in logging memory.")

    # --- TAB: ORDER LOOKUP BY ID OR PHONE ---
    with tab_track:
        st.markdown("### System Pipeline Diagnostic Registry")
        user_query_input = st.text_input("Input Order Code or Customer Phone Number:", placeholder="TF-WEB-1234 or 863-555-0199").strip()
        
        if st.button("Query Database"):
            if user_query_input:
                try:
                    conn = get_db_connection()
                    clean_input = user_query_input.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                    query = """
                        SELECT * FROM orders_v2 
                        WHERE order_id = ? 
                        OR phone_number = ?
                        OR REPLACE(REPLACE(REPLACE(REPLACE(phone_number, '-', ''), ' ', ''), '(', ''), ')', '') LIKE ?
                        ORDER BY timestamp DESC
                    """
                    results = conn.execute(query, (user_query_input, user_query_input, f"%{clean_input}%")).fetchall()
                    conn.close()
                    
                    if results:
                        st.markdown(f"### Diagnostic Result: Found {len(results)} Matching Order(s) ✅")
                        
                        # Display results in a table
                        results_data = [dict(r) for r in results]
                        st.dataframe(pd.DataFrame(results_data), use_container_width=True)
                    else:
                        st.error("No transaction found matching that ID or Phone Number.")
                except Exception as e:
                    st.error("Database error while processing lookup request.")
            else:
                st.warning("Please enter an Order ID or Phone Number.")

    # --- COMPLETE GLOBAL FINANCIAL LEDGER MATRIX WITH 30-DAY TRUCKING ---
    with tab_ops:
        st.markdown("### Complete Global Financial Ledger Matrix")
        try:
            conn = get_db_connection()
            df_orders = pd.read_sql_query("SELECT * FROM orders_v2 ORDER BY timestamp DESC", conn)
            conn.close()
            
            if not df_orders.empty:
                # --- 30-DAY TIMEFRAME CALCULATOR ---
                df_orders['parsed_time'] = pd.to_datetime(df_orders['timestamp'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
                
                thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
                df_30_days = df_orders[df_orders['parsed_time'] >= thirty_days_ago]
                
                # Metrics Display Summary
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("30-Day Total Orders", len(df_30_days))
                with col_m2:
                    st.metric("30-Day Revenue Metric", f"${df_30_days['total_paid'].sum():.2f}")
                with col_m3:
                    st.metric("30-Day Bottles Sold", int(df_30_days['quantity'].sum()) if 'quantity' in df_30_days.columns else len(df_30_days))
                
                st.markdown("---")
                
                # Interactive Ledger Filter checkbox
                show_only_30_days = st.checkbox("📅 Filter Matrix Ledger view to past 30 days only", value=False)
                
                display_df = df_30_days if show_only_30_days else df_orders
                if 'parsed_time' in display_df.columns:
                    display_df = display_df.drop(columns=['parsed_time'])
                    
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("The business database log is empty.")
        except Exception as e:
            st.info("The business database log is empty.")

# --- GLOBAL FOOTER (LEGAL DISCLAIMER & COPYRIGHT) ---
st.markdown("---")
st.markdown(
    """
    <div style='font-size: 0.8rem; color: #64748B; text-align: justify; line-height: 1.4; margin-bottom: 20px;'>
    <strong>LEGAL DISCLAIMER:</strong> T Fragrances competes with the designer brands. It does not use their 
    fragrances and is not associated or affiliated in any way with the designer brands or their manufacturers. 
    All trademarks are the property of their respective owners. We use designer names solely for comparative 
    purposes to give customers an idea of the scent character and olfactory notes.<br><br>
    <strong>ALLERGY & SENSITIVITY NOTICE:</strong> Our products contain fragrance oils and ingredients that may cause skin irritation or allergic reactions in sensitive individuals. Please review ingredient lists carefully and perform a patch test prior to full application. Discontinue use immediately if irritation occurs. T Fragrances is not responsible for any adverse reactions.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style='text-align: center; color: #FFFFFF; font-size: 0.9rem; margin-top: 10px;'>
    © T Fragrances. All Rights Reserved.
    </p>
    """, 
    unsafe_allow_html=True
)
