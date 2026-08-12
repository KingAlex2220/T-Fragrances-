import streamlit as st
import sqlite3
import datetime
import time
import os
import pandas as pd

# --- PAGE SETUP & AMAZON E-COMMERCE THEMING ---
st.set_page_config(page_title="T Fragrances | Luxury Oil Marketplace", page_icon="📦", layout="wide")

st.markdown("""
<style>
    /* Amazon-inspired dark navbar header */
    .nav-bar {
        background-color: #131921;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        margin-bottom: 20px;
    }
    .brand-title {
        font-size: 2rem;
        font-weight: 800;
        color: #FF9900;
        margin: 0;
        letter-spacing: 1px;
    }
    .brand-tagline {
        color: #CCCCCC;
        font-size: 0.85rem;
        margin: 0;
    }
    /* Product card styling */
    .product-card {
        border: 1px solid #DDD;
        border-radius: 8px;
        padding: 15px;
        background-color: #FFFFFF;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .price-tag {
        font-size: 1.5rem;
        font-weight: bold;
        color: #B12704;
    }
    .badge-prime {
        background-color: #00A8E1;
        color: white;
        font-size: 0.75rem;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 3px;
    }
    .badge-in-stock {
        color: #007600;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .badge-preorder {
        color: #C45500;
        font-weight: bold;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP ---
DB_FILE = "t_fragrances.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- MASTER CATALOG ---
men_catalog = [
    {"code": "NO-1", "label": "No 1 | Sauvage Blend", "scent": "No 1 Sauvage Blend", "category": "Men's Premium Oils", "rating": "⭐⭐⭐⭐⭐ (4.9)", "desc": "Fresh, spicy, and woody 100% pure oil blend."},
    {"code": "NO-4", "label": "No 4 | Aventus Blend", "scent": "No 4 Aventus Blend", "category": "Men's Premium Oils", "rating": "⭐⭐⭐⭐⭐ (5.0)", "desc": "Rich, smoky pineapple and birch signature blend."},
]

women_catalog = [
    {"code": "NO-2", "label": "No 2 | Good Girl Blend", "scent": "No 2 Good Girl Blend", "category": "Women's Premium Oils", "rating": "⭐⭐⭐⭐⭐ (4.8)", "desc": "Sweet jasmine, cocoa, and tonka bean elegant blend."},
    {"code": "NO-3", "label": "No 3 | Rouge 540 Blend", "scent": "No 3 Rouge 540 Blend", "category": "Women's Premium Oils", "rating": "⭐⭐⭐⭐⭐ (5.0)", "desc": "Luminous saffron, amberwood, and fir resin luxury oil."},
]

home_catalog = [
    {"code": "H#1", "label": "H#1 | Laundry Day", "scent": "Laundry Day", "category": "Home & House Scents", "rating": "⭐⭐⭐⭐☆ (4.7)", "desc": "Crisp, clean linen notes engineered to refresh any space."},
    {"code": "H#2", "label": "H#2 | Sunrise", "scent": "Sunrise", "category": "Home & House Scents", "rating": "⭐⭐⭐⭐⭐ (4.9)", "desc": "Bright citrus notes blended with warm morning amber."},
]

ALL_CATALOG_ITEMS = men_catalog + women_catalog + home_catalog
DEFAULT_INITIAL_STOCK = 5
PRICE_PER_BOTTLE = 45.00

LOCAL_BOTTLE_IMG = "images/bottles.png"
LOCAL_QR_IMG = "images/zelle_qr.png"
LOCAL_CASHAPP_QR_IMG = "images/cashapp_qr.png"
LOCAL_VENMO_QR_IMG = "images/venmo_qr.png"
LOCAL_CATALOG_QR_IMG = "images/Catalog_qr.png.jpg"

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
            quantity INTEGER DEFAULT 1,
            total_paid REAL,
            payment_method TEXT,
            is_preorder INTEGER DEFAULT 0,
            status TEXT,
            order_type TEXT DEFAULT 'Online Store'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_code TEXT PRIMARY KEY,
            category TEXT,
            scent_name TEXT,
            stock_quantity INTEGER DEFAULT 5,
            initial_capacity INTEGER DEFAULT 5
        )
    """)
    for item in ALL_CATALOG_ITEMS:
        cursor.execute("""
            INSERT OR IGNORE INTO inventory (product_code, category, scent_name, stock_quantity, initial_capacity)
            VALUES (?, ?, ?, ?, ?)
        """, (item["code"], item["category"], item["scent"], DEFAULT_INITIAL_STOCK, DEFAULT_INITIAL_STOCK))
    conn.commit()
    conn.close()

init_db()

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

# --- CART INITIALIZATION ---
if "cart" not in st.session_state:
    st.session_state.cart = {}

# --- SIDEBAR ACCESS INTERFACE ---
st.sidebar.markdown("### 🔒 System Portal")
access_mode = "🛍️ Amazon Storefront"

with st.sidebar.expander("Staff Portal", expanded=False):
    password = st.text_input("Enter Admin Password:", type="password", key="admin_password_input")

if password == "Safe9uard-tf80":
    st.sidebar.success("Authenticated")
    access_mode = st.sidebar.radio("View Mode", ["🛍️ Amazon Storefront", "💼 Owner Hub & POS"])
elif password:
    st.sidebar.error("Incorrect Password")

# ==========================================
# PUBLIC VIEW: AMAZON E-COMMERCE STOREFRONT
# ==========================================
if access_mode == "🛍️ Amazon Storefront":
    
    # Header Banner
    st.markdown("""
    <div class="nav-bar">
        <span class="brand-title">T FRAGRANCES</span>
        <span style="float:right; font-size: 0.9rem; margin-top: 8px;">FREE FAST SHIPPING OVER $100</span>
        <p class="brand-tagline">Designer Quality (50ml) | 100% Pure Oil-Based | Reimagined Luxury</p>
    </div>
    """, unsafe_allow_html=True)
    
    cart_count = sum(item["qty"] for item in st.session_state.cart.values())
    
    # Top Navigation / Utility Bar
    col_search, col_track, col_cart_btn = st.columns([3, 1, 1])
    with col_search:
        search_query = st.text_input("🔍 Search Amazon-style Catalog...", placeholder="Search Sauvage, Aventus, Sunrise...", label_visibility="collapsed")
    with col_track:
        show_tracker = st.checkbox("📦 Track Order")
    with col_cart_btn:
        st.markdown(f"#### 🛒 Cart ({cart_count})")

    st.markdown("---")

    if show_tracker:
        st.subheader("📦 Real-Time Order Tracking")
        cust_query_input = st.text_input("Enter Order ID or Phone Number:", key="track_search").strip()
        if st.button("Find Order"):
            if cust_query_input:
                conn = get_db_connection()
                clean = cust_query_input.replace("-", "").replace(" ", "")
                query = "SELECT * FROM orders_v2 WHERE order_id = ? OR phone_number = ? ORDER BY timestamp DESC"
                rows = conn.execute(query, (cust_query_input, cust_query_input)).fetchall()
                conn.close()
                if rows:
                    for row in rows:
                        st.info(f"Order `{row['order_id']}` | Status: **{row['status']}** | Total: ${row['total_paid']:.2f}")
                else:
                    st.error("No orders found.")
        st.markdown("---")

    if "last_order_details" in st.session_state:
        order_info = st.session_state.last_order_details
        st.balloons()
        st.success(f"🎉 Order Confirmed! Order ID: `{order_info['id']}`")
        
        with st.expander("💳 Payment Settlement Instructions", expanded=True):
            method = order_info["method"]
            tot = order_info["total"]
            oid = order_info["id"]
            
            st.markdown(f"### Total Due: **${tot:.2f}** via **{method}**")
            if method == "Zelle":
                st.info(f"Send to **863-236-4196** (Alexander Thompson)\nMemo: `{oid}`")
                if os.path.exists(LOCAL_QR_IMG): st.image(LOCAL_QR_IMG, width=250)
            elif method == "Cash App":
                st.info(f"Send to `$JaMekaHowell` (Jameka Howell)\nMemo: `{oid}`")
                if os.path.exists(LOCAL_CASHAPP_QR_IMG): st.image(LOCAL_CASHAPP_QR_IMG, width=250)
            elif method == "Venmo":
                st.info(f"Send to `@Jameka-Hatton` (Jameka Hatton)\nMemo: `{oid}`")
                if os.path.exists(LOCAL_VENMO_QR_IMG): st.image(LOCAL_VENMO_QR_IMG, width=250)
            else:
                st.info(f"Send Apple Pay to **863-236-4196**\nNote: `{oid}`")
            
            st.warning("⚠️ Include your Order ID in the payment memo!")
            
        if st.button("Continue Shopping"):
            del st.session_state.last_order_details
            st.rerun()

    else:
        main_layout, cart_layout = st.columns([3, 1.2])

        # --- PRODUCT CATALOG GRID ---
        with main_layout:
            tab_all, tab_men, tab_women, tab_home, tab_custom = st.tabs(["✨ All Scents", "👔 Men's", "👗 Women's", "🏠 House Scents", "📜 Full Catalog Request"])

            def render_grid(items):
                filtered = [i for i in items if search_query.lower() in i["scent"].lower() or search_query.lower() in i["category"].lower()]
                if not filtered:
                    st.info("No matching fragrances found.")
                    return

                for idx in range(0, len(filtered), 2):
                    cols = st.columns(2)
                    for c_idx, item in enumerate(filtered[idx:idx+2]):
                        stock, cap = get_item_stock(item["code"])
                        is_preorder = stock <= 0
                        
                        with cols[c_idx]:
                            with st.container(border=True):
                                if os.path.exists(LOCAL_BOTTLE_IMG):
                                    st.image(LOCAL_BOTTLE_IMG, use_container_width=True)
                                st.markdown(f"#### {item['scent']}")
                                st.caption(f"{item['rating']} | Category: {item['category']}")
                                st.write(item["desc"])
                                st.markdown(f"<span class='price-tag'>${PRICE_PER_BOTTLE:.2f}</span> <span class='badge-prime'>FREE EXPRESS</span>", unsafe_allow_html=True)
                                
                                if is_preorder:
                                    st.markdown("<span class='badge-preorder'>⭐ Priority Preorder Available</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<span class='badge-in-stock'>In Stock ({stock} left)</span>", unsafe_allow_html=True)

                                col_q, col_b = st.columns([1, 2])
                                with col_q:
                                    q_val = st.number_input("Qty", min_value=1, max_value=50 if is_preorder else max(1, stock), value=1, key=f"q_{item['code']}")
                                with col_b:
                                    st.write("")
                                    if st.button("Add to Cart 🛒", key=f"btn_{item['code']}", use_container_width=True):
                                        code = item["code"]
                                        if code in st.session_state.cart:
                                            st.session_state.cart[code]["qty"] += q_val
                                        else:
                                            st.session_state.cart[code] = {
                                                "code": code,
                                                "scent": item["scent"],
                                                "category": item["category"],
                                                "qty": q_val,
                                                "price": PRICE_PER_BOTTLE,
                                                "is_preorder": 1 if is_preorder else 0
                                            }
                                        st.toast(f"Added {q_val}x {item['scent']} to cart!", icon="🛒")
                                        time.sleep(0.3)
                                        st.rerun()

            with tab_all: render_grid(ALL_CATALOG_ITEMS)
            with tab_men: render_grid(men_catalog)
            with tab_women: render_grid(women_catalog)
            with tab_home: render_grid(home_catalog)
            with tab_custom:
                st.info("✨ Don't see your scent? Type any designer fragrance name to place a custom order!")
                if os.path.exists(LOCAL_CATALOG_QR_IMG):
                    st.image(LOCAL_CATALOG_QR_IMG, caption="Scan for Extended Catalog", width=200)
                custom_scent = st.text_input("Fragrance & Brand Name:")
                custom_qty = st.number_input("Quantity:", min_value=1, value=1, key="c_qty")
                if st.button("Add Custom Request to Cart"):
                    if custom_scent.strip():
                        code = f"CUSTOM-{int(time.time())}"
                        st.session_state.cart[code] = {
                            "code": "CUSTOM-REQ",
                            "scent": custom_scent.strip(),
                            "category": "Custom Request",
                            "qty": custom_qty,
                            "price": PRICE_PER_BOTTLE,
                            "is_preorder": 1
                        }
                        st.success("Custom request added to cart!")
                        st.rerun()

        # --- SHOPPING CART & CHECKOUT PANEL ---
        with cart_layout:
            with st.container(border=True):
                st.markdown("### 🛒 Shopping Cart")
                if not st.session_state.cart:
                    st.info("Your Amazon cart is empty.")
                else:
                    subtotal = 0.0
                    to_remove = []
                    
                    for code, item in st.session_state.cart.items():
                        line_total = item["price"] * item["qty"]
                        subtotal += line_total
                        
                        st.markdown(f"**{item['scent']}**")
                        c1, c2, c3 = st.columns([2, 2, 1])
                        with c1: st.caption(f"${item['price']:.2f} x {item['qty']}")
                        with c2: st.write(f"**${line_total:.2f}**")
                        with c3:
                            if st.button("❌", key=f"del_{code}"):
                                to_remove.append(code)
                        st.markdown("---")
                    
                    for code in to_remove:
                        del st.session_state.cart[code]
                        st.rerun()

                    # Volume Discount: > $100 gets 20% off
                    discount = subtotal * 0.20 if subtotal > 100.00 else 0.0
                    final_total = subtotal - discount

                    st.write(f"Subtotal: **${subtotal:.2f}**")
                    if discount > 0:
                        st.success(f"20% Discount Applied: **-${discount:.2f}**")
                    st.markdown(f"### Total: **${final_total:.2f}**")

                    st.markdown("---")
                    st.markdown("### 📦 Delivery Address")
                    c_name = st.text_input("Full Name:", key="checkout_name")
                    c_phone = st.text_input("Phone Number:", key="checkout_phone")
                    c_address = st.text_area("Shipping Address:", key="checkout_addr")
                    c_pay = st.selectbox("Payment Channel:", ["Zelle", "Cash App", "Venmo", "Apple Pay"])

                    if st.button("Proceed to Checkout", type="primary", use_container_width=True):
                        if not c_name.strip() or not c_phone.strip() or not c_address.strip():
                            st.error("Please complete your delivery details.")
                        else:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            batch_id = f"TF-AMZ-{int(time.time())}"
                            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            # Store cart items as individual database entries
                            for code, item in st.session_state.cart.items():
                                item_total = (item["price"] * item["qty"]) * (0.80 if subtotal > 100.00 else 1.0)
                                is_pre = item.get("is_preorder", 0)
                                status = "Preorder - Awaiting Batch Restock" if is_pre else "Awaiting Settlement"

                                cursor.execute("""
                                    INSERT INTO orders_v2 
                                    (order_id, timestamp, customer_name, phone_number, delivery_address, category, product_code, scent_name, quantity, total_paid, payment_method, is_preorder, status, order_type)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    batch_id, ts, c_name.strip(), c_phone.strip(), c_address.strip(),
                                    item["category"], item["code"], item["scent"], item["qty"], item_total,
                                    c_pay, is_pre, status, 'Online Store'
                                ))

                                if not is_pre:
                                    deduct_inventory(item["code"], item["qty"])

                            conn.commit()
                            conn.close()

                            st.session_state.last_order_details = {
                                "id": batch_id,
                                "total": final_total,
                                "method": c_pay
                            }
                            st.session_state.cart = {}
                            st.rerun()

# ==========================================
# PRIVATE VIEW: OWNER HUB & POS TERMINAL
# ==========================================
else:
    st.subheader("💼 Master Business Operations Hub")
    
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
                st.error(f"🚨 **{row['product_code']} - {row['scent_name']}**: OUT OF STOCK")
            else:
                st.write(f"⚠️ **{row['product_code']} - {row['scent_name']}**: {row['stock_quantity']} units left")
        st.markdown("---")

    tab_preorders, tab_pos, tab_inventory, tab_web_orders, tab_track, tab_ops = st.tabs([
        "⭐ Priority Preorders Queue",
        "🛒 In-Person POS Terminal", 
        "📦 Inventory Tracker", 
        "📬 Pending Web Orders", 
        "📦 Order Lookup", 
        "🛡️ Master Database Ledger"
    ])
    
    with tab_preorders:
        st.markdown("### ⭐ Priority Preorder Fulfillment Queue")
        conn = get_db_connection()
        preorders_df = pd.read_sql_query("SELECT order_id, timestamp, customer_name, phone_number, delivery_address, product_code, scent_name, quantity, payment_method, total_paid, status FROM orders_v2 WHERE is_preorder = 1 ORDER BY timestamp ASC", conn)
        conn.close()
        
        if preorders_df.empty:
            st.success("🎉 No pending preorders in queue!")
        else:
            st.dataframe(preorders_df, use_container_width=True)
            col_p1, col_p2 = st.columns([2, 1])
            with col_p1:
                target_preorder = st.selectbox("Select Priority Preorder ID to Process:", preorders_df["order_id"].unique().tolist())
            with col_p2:
                preorder_action = st.radio("Preorder Status Update:", ["Mark as Batch Restocked & Processing", "Mark as Shipped / Completed", "Cancel Preorder"])
                
            if st.button("Update Preorder Status"):
                new_p_status = "Paid & Processing" if "Processing" in preorder_action else ("Completed & Shipped" if "Completed" in preorder_action else "Cancelled")
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
            if "pos_cart" in st.session_state and st.session_state.pos_cart:
                cart = st.session_state.pos_cart
                st.metric("Immediate Cash Flow Collected", f"${cart['price']:.2f}")
                st.write(f"• **Customer:** {cart['client']}")
                st.write(f"• **Scent:** {cart['scent']} ({cart['quantity']} Unit(s))")
                
                if st.button("Commit Sale to Ledger"):
                    generated_id = f"TF-POS-{int(time.time())}"
                    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    pos_status = "Preorder Recorded (In-Person)" if cart.get("is_preorder") == 1 else "Completed & Handed Over"
                    
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO orders_v2 (order_id, timestamp, customer_name, phone_number, delivery_address, category, product_code, scent_name, quantity, total_paid, payment_method, is_preorder, status, order_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (generated_id, timestamp_str, cart['client'], cart['phone'], 'In-Person Sale', cart['category'], cart['code'], cart['scent'], cart['quantity'], cart['price'], cart['vector'], cart.get("is_preorder", 0), pos_status, "POS Register"))
                    conn.commit()
                    conn.close()
                    
                    if cart.get("is_preorder") == 0:
                        deduct_inventory(cart['code'], cart['quantity'])
                    
                    st.success(f"Transaction Recorded! Code: {generated_id}")
                    st.session_state.pos_cart = None
                    st.rerun()

    with tab_inventory:
        st.markdown("### 📦 Inventory Stock Levels")
        conn = get_db_connection()
        inv_df = pd.read_sql_query("SELECT product_code AS Code, category AS Category, scent_name AS Scent, stock_quantity AS 'Stock Left', initial_capacity AS Capacity FROM inventory", conn)
        conn.close()
        st.dataframe(inv_df, use_container_width=True)
        
        col_r1, col_r2, col_r3 = st.columns([2, 1, 1])
        with col_r1:
            item_to_restock = st.selectbox("Select Scent to Restock:", [f"{item['code']} - {item['scent']}" for item in ALL_CATALOG_ITEMS])
        with col_r2:
            add_amount = st.number_input("Quantity to Add:", min_value=1, max_value=500, value=10, step=1)
        with col_r3:
            if st.button("Update Stock"):
                target_code = item_to_restock.split(" - ")[0]
                conn = get_db_connection()
                conn.execute("UPDATE inventory SET stock_quantity = stock_quantity + ? WHERE product_code = ?", (int(add_amount), target_code))
                conn.commit()
                conn.close()
                st.success(f"Added {add_amount} units to {target_code}!")
                st.rerun()

    with tab_web_orders:
        st.markdown("### Online Orders Awaiting Verification")
        conn = get_db_connection()
        pending_df = pd.read_sql_query("SELECT order_id, timestamp, customer_name, phone_number, product_code, scent_name, quantity, payment_method, total_paid, status, is_preorder FROM orders_v2 WHERE order_type = 'Online Store' AND (status LIKE 'Awaiting%' OR status LIKE '%Preorder%')", conn)
        conn.close()
        if pending_df.empty:
            st.success("No pending web orders require attention.")
        else:
            st.dataframe(pending_df, use_container_width=True)
            target_order = st.selectbox("Select Order ID to update:", pending_df["order_id"].unique().tolist())
            next_action = st.radio("Action:", ["Mark as Paid & Ready to Pack/Ship", "Convert to Priority Preorder Queue", "Cancel / Payment Rejected"])
            if st.button("Execute Action Update"):
                new_status = "Paid & Processing" if "Mark as Paid" in next_action else ("Preorder - Awaiting Batch Restock" if "Convert" in next_action else "Cancelled")
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE orders_v2 SET status = ?, is_preorder = ? WHERE order_id = ?", (new_status, 1 if "Preorder" in new_status else 0, target_order))
                conn.commit()
                conn.close()
                st.success(f"Order {target_order} updated!")
                st.rerun()

    with tab_track:
        st.markdown("### System Pipeline Diagnostic Registry")
        user_query_input = st.text_input("Input Order Code or Customer Phone Number:", placeholder="TF-AMZ-1234").strip()
        if st.button("Query Database"):
            if user_query_input:
                conn = get_db_connection()
                results = conn.execute("SELECT * FROM orders_v2 WHERE order_id = ? OR phone_number = ?", (user_query_input, user_query_input)).fetchall()
                conn.close()
                if results:
                    st.dataframe(pd.DataFrame([dict(r) for r in results]), use_container_width=True)
                else:
                    st.error("No transaction found.")

    with tab_ops:
        st.markdown("### Complete Global Financial Ledger Matrix")
        conn = get_db_connection()
        df_orders = pd.read_sql_query("SELECT * FROM orders_v2 ORDER BY timestamp DESC", conn)
        conn.close()
        if not df_orders.empty:
            st.dataframe(df_orders, use_container_width=True)
        else:
            st.info("Ledger empty.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748B; font-size: 0.85rem;'>© T Fragrances Storefront. Amazon-style e-commerce portal powered by Streamlit & SQLite.</p>", unsafe_allow_html=True)
