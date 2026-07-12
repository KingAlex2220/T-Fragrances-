import streamlit as st
import sqlite3
import random
import datetime
import os

# --- PAGE SETUP & BRANDING ---
st.set_page_config(page_title="T Fragrances - POS & Tracking", page_icon="✨", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E293B; font-family: \"Segoe UI\", sans-serif; margin-bottom: 0;'>T FRAGRANCES</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #64748B; font-size: 1.1rem; margin-top: 5px;'>Designer Quality | 100% Pure Oil-Based | Reimagined Luxury</p>", unsafe_allow_html=True)
st.markdown("---")

# --- DATA STORAGE SETUP (SQLite) ---
DB_FILE = "t_fragrances.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            timestamp TEXT,
            customer_name TEXT,
            category TEXT,
            product_code TEXT,
            scent_name TEXT,
            payment_method TEXT,
            total_paid REAL,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- LIGHTWEIGHT TEXT INVENTORY LOADER ---
@st.cache_data
def load_catalog_data():
    men_items = []
    women_items = []
    home_items = []

    # 1. Men's Text Catalog
    if os.path.exists('mens_catalog.txt'):
        with open('mens_catalog.txt', 'r') as f:
            for line in f:
                if line.strip() and '|' in line:
                    parts = line.split('|')
                    code = parts[0].strip()
                    brand = parts[1].strip() if len(parts) > 1 else 'UNKNOWN'
                    scent = parts[2].strip() if len(parts) > 2 else 'UNKNOWN'
                    men_items.append({"code": code, "label": f"{code} | {brand} - {scent}", "scent": scent})

    # 2. Women's Text Catalog
    if os.path.exists('womens_catalog.txt'):
        with open('womens_catalog.txt', 'r') as f:
            for line in f:
                if line.strip() and '|' in line:
                    parts = line.split('|')
                    code = parts[0].strip()
                    brand = parts[1].strip() if len(parts) > 1 else 'UNKNOWN'
                    scent = parts[2].strip() if len(parts) > 2 else 'UNKNOWN'
                    women_items.append({"code": code, "label": f"{code} | {brand} - {scent}", "scent": scent})

    # 3. Home Scents Text Catalog
    if os.path.exists('home_catalog.txt'):
        with open('home_catalog.txt', 'r') as f:
            for line in f:
                if line.strip() and '|' in line:
                    parts = line.split('|')
                    code = parts[0].strip()
                    scent = parts[1].strip() if len(parts) > 1 else 'UNKNOWN'
                    home_items.append({"code": code, "label": f"{code} | House Blend - {scent}", "scent": scent})

    # Emergency Fallbacks if files are empty
    if not men_items:
        men_items = [{"code": "#48E", "label": "#48E | Creed - Aventus", "scent": "Aventus"}]
    if not women_items:
        women_items = [{"code": "#15A", "label": "#15A | BACCARAT - ROUGE 540", "scent": "ROUGE 540"}]
    if not home_items:
        home_items = [{"code": "H#1", "label": "H#1 | House Blend - 4 EVER SUN", "scent": "4 EVER SUN"}]

    return men_items, women_items, home_items

men_catalog, women_catalog, home_catalog = load_catalog_data()
PRICE_SHEET = {"Men's Premium Oils": 80.00, "Women's Premium Oils": 80.00, "Home & House Scents": 30.00}

# --- NAVIGATION TABS ---
tab_pos, tab_track, tab_ops = st.tabs(["🛒 Register & Digital POS", "📦 Track Client Order", "🛡️ Admin Operations Management"])

# ==========================================
# TAB 1: POINT OF SALE TERMINAL
# ==========================================
with tab_pos:
    st.subheader("Point of Sale Terminal")
    col_entry, col_invoice = st.columns([3, 2])
    
    with col_entry:
        with st.container(border=True):
            st.markdown("#### 1. Select Product Family")
            cat_select = st.radio("Line Segment:", ["Men's Premium Oils", "Women's Premium Oils", "Home & House Scents"], horizontal=True)
            
            if cat_select == "Men's Premium Oils":
                active_list = men_catalog
            elif cat_select == "Women's Premium Oils":
                active_list = women_catalog
            else:
                active_list = home_catalog
                
            st.markdown("#### 2. Scan / Match Alphanumeric Code")
            selected_display = st.selectbox("Search master index:", [item["label"] for item in active_list])
            
            matching_obj = next(item for item in active_list if item["label"] == selected_display)
            
            st.markdown("#### 3. Checkout Data Ingestion")
            client_name = st.text_input("Customer Name:", placeholder="Jane Doe")
            payment_vector = st.selectbox("Digital Settlement Channel:", ["Apple Pay", "Venmo", "Cash App", "Credit Card Swipe", "Zelle", "Cash"])
            
            generate_click = st.button("Generate Invoice Configuration", type="primary")
            
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
                    "price": PRICE_SHEET[cat_select]
                }
                
    with col_invoice:
        st.markdown("#### 🧾 Live Transaction Processing")
        if "pos_cart" in st.session_state and st.session_state.pos_cart is not None:
            cart = st.session_state.pos_cart
            st.warning(f"**Awaiting Authorization via {cart['vector']}**")
            st.metric("Total Line Settlement Due", f"${cart['price']:.2f}")
            st.write(f"• **Purchaser:** {cart['client']}")
            st.write(f"• **Alphanumeric Code Mapping:** {cart['code']}")
            st.write(f"• **Scent Formulation Blueprint:** {cart['scent']}")
            
            if st.button("Post Settlement Clear (Process Order)"):
                generated_id = f"TF-{random.randint(10000, 99999)}"
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO orders (order_id, timestamp, customer_name, category, product_code, scent_name, payment_method, total_paid, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (generated_id, timestamp_str, cart['client'], cart['category'], cart['code'], cart['scent'], cart['vector'], cart['price'], "Processing"))
                conn.commit()
                conn.close()
                
                st.success(f"Transaction Cleared! Tracking Code: {generated_id}")
                st.balloons()
                st.session_state.pos_cart = None
        else:
            st.info("Terminal completely clear.")

# ==========================================
# TAB 2: TRACKING PORTAL
# ==========================================
with tab_track:
    st.subheader("Customer Order Fulfillment Tracking")
    user_query_input = st.text_input("Input Your Tracking Code:", placeholder="TF-43210").strip()
    
    if st.button("Run Pipeline Diagnostic Query"):
        if user_query_input:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (user_query_input,)).fetchone()
            conn.close()
            if row:
                st.markdown(f"### Update Diagnostic: Order Found ✅")
                st.metric("Current Production Progress Status", row["status"])
                st.write(f"**Customer Account:** {row['customer_name']} | **Formula Target:** {row['scent_name']}")
            else:
                st.error("No transaction matching that serial code was found.")

# ==========================================
# TAB 3: ADMIN PORTAL
# ==========================================
with tab_ops:
    st.subheader("Internal Business Management Panel")
    conn = get_db_connection()
    import pandas as pd
    df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    
    if not df_orders.empty:
        st.dataframe(df_orders, use_container_width=True)
fixed storefront routing script
