import streamlit as st
import sqlite3
import random
import datetime
import time
import os
import pandas as pd

# --- PAGE SETUP & BRANDING ---
st.set_page_config(page_title="T Fragrances - Storefront & POS", page_icon="✨", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E293B; font-family: \"Segoe UI\", sans-serif; margin-bottom: 0;'>T FRAGRANCES</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #64748B; font-size: 1.1rem; margin-top: 5px;'>Designer Quality (50ml) | 100% Pure Oil-Based | Reimagined Luxury</p>", unsafe_allow_html=True)
st.markdown("---")

# --- DATA STORAGE SETUP ---
DB_FILE = "t_fragrances.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- EMBEDDED MASTER CATALOG (FULL 60 IMPRESSIONS: 30 MEN / 30 WOMEN) ---
men_catalog = [
    {"code": "NO-1", "label": "No 1 | Sauvage Blend", "scent": "Sauvage Blend", "category": "Men's Premium Oils"},
    {"code": "NO-4", "label": "No 4 | Aventus Blend", "scent": "Aventus Blend", "category": "Men's Premium Oils"},
    {"code": "NO-5", "label": "No 5 | Bleu de Chanel Blend", "scent": "Bleu de Chanel Blend", "category": "Men's Premium Oils"},
    {"code": "NO-6", "label": "No 6 | Acqua di Giò Blend", "scent": "Acqua di Giò Blend", "category": "Men's Premium Oils"},
    {"code": "NO-7", "label": "No 7 | Eros Blend", "scent": "Eros Blend", "category": "Men's Premium Oils"},
    {"code": "NO-8", "label": "No 8 | One Million Blend", "scent": "One Million Blend", "category": "Men's Premium Oils"},
    {"code": "NO-9", "label": "No 9 | Spicebomb Blend", "scent": "Spicebomb Blend", "category": "Men's Premium Oils"},
    {"code": "NO-10", "label": "No 10 | YSL Y Blend", "scent": "YSL Y Blend", "category": "Men's Premium Oils"},
    {"code": "NO-11", "label": "No 11 | Tom Ford Oud Wood Blend", "scent": "Tom Ford Oud Wood Blend", "category": "Men's Premium Oils"},
    {"code": "NO-12", "label": "No 12 | Chrome Legend Blend", "scent": "Chrome Legend Blend", "category": "Men's Premium Oils"},
    {"code": "NO-13", "label": "No 13 | Gucci Guilty Blend", "scent": "Gucci Guilty Blend", "category": "Men's Premium Oils"},
    {"code": "NO-14", "label": "No 14 | Bvlgari Aqva Blend", "scent": "Bvlgari Aqva Blend", "category": "Men's Premium Oils"},
    {"code": "NO-15", "label": "No 15 | Playboy New York Blend", "scent": "Playboy New York Blend", "category": "Men's Premium Oils"},
    {"code": "NO-16", "label": "No 16 | Invictus Blend", "scent": "Invictus Blend", "category": "Men's Premium Oils"},
    {"code": "NO-17", "label": "No 17 | Creed Silver Mountain Water Blend", "scent": "Creed Silver Mountain Water Blend", "category": "Men's Premium Oils"},
    {"code": "NO-31", "label": "No 31 | Tobacco Vanille Blend", "scent": "Tobacco Vanille Blend", "category": "Men's Premium Oils"},
    {"code": "NO-32", "label": "No 32 | Le Male Blend", "scent": "Le Male Blend", "category": "Men's Premium Oils"},
    {"code": "NO-33", "label": "No 33 | Polo Red Blend", "scent": "Polo Red Blend", "category": "Men's Premium Oils"},
    {"code": "NO-34", "label": "No 34 | Santal 33 Blend", "scent": "Santal 33 Blend", "category": "Men's Premium Oils"},
    {"code": "NO-35", "label": "No 35 | Wanted Blend", "scent": "Wanted Blend", "category": "Men's Premium Oils"},
    {"code": "NO-36", "label": "No 36 | Gentleman Blend", "scent": "Gentleman Blend", "category": "Men's Premium Oils"},
    {"code": "NO-37", "label": "No 37 | Light Blue Pour Homme Blend", "scent": "Light Blue Pour Homme Blend", "category": "Men's Premium Oils"},
    {"code": "NO-38", "label": "No 38 | Allure Homme Sport Blend", "scent": "Allure Homme Sport Blend", "category": "Men's Premium Oils"},
    {"code": "NO-39", "label": "No 39 | L'Homme Ideal Blend", "scent": "L'Homme Ideal Blend", "category": "Men's Premium Oils"},
    {"code": "NO-40", "label": "No 40 | Diesel Only The Brave Blend", "scent": "Diesel Only The Brave Blend", "category": "Men's Premium Oils"},
    {"code": "NO-41", "label": "No 41 | Montblanc Legend Blend", "scent": "Montblanc Legend Blend", "category": "Men's Premium Oils"},
    {"code": "NO-42", "label": "No 42 | Prada L'Homme Blend", "scent": "Prada L'Homme Blend", "category": "Men's Premium Oils"},
    {"code": "NO-43", "label": "No 43 | Valentino Uomo Born In Roma Blend", "scent": "Valentino Uomo Born In Roma Blend", "category": "Men's Premium Oils"},
    {"code": "NO-44", "label": "No 44 | Bad Boy Blend", "scent": "Bad Boy Blend", "category": "Men's Premium Oils"},
    {"code": "NO-45", "label": "No 45 | 1 Million Lucky Blend", "scent": "1 Million Lucky Blend", "category": "Men's Premium Oils"},
]

women_catalog = [
    {"code": "NO-2", "label": "No 2 | Good Girl Blend", "scent": "Good Girl Blend", "category": "Women's Premium Oils"},
    {"code": "NO-3", "label": "No 3 | Baccarat Rouge 540 Blend", "scent": "Baccarat Rouge 540 Blend", "category": "Women's Premium Oils"},
    {"code": "NO-18", "label": "No 18 | Black Opium Blend", "scent": "Black Opium Blend", "category": "Women's Premium Oils"},
    {"code": "NO-19", "label": "No 19 | La Vie Est Belle Blend", "scent": "La Vie Est Belle Blend", "category": "Women's Premium Oils"},
    {"code": "NO-20", "label": "No 20 | Coco Mademoiselle Blend", "scent": "Coco Mademoiselle Blend", "category": "Women's Premium Oils"},
    {"code": "NO-21", "label": "No 21 | Flowerbomb Blend", "scent": "Flowerbomb Blend", "category": "Women's Premium Oils"},
    {"code": "NO-22", "label": "No 22 | J'adore Blend", "scent": "J'adore Blend", "category": "Women's Premium Oils"},
    {"code": "NO-23", "label": "No 23 | Miss Dior Blend", "scent": "Miss Dior Blend", "category": "Women's Premium Oils"},
    {"code": "NO-24", "label": "No 24 | Versace Bright Crystal Blend", "scent": "Versace Bright Crystal Blend", "category": "Women's Premium Oils"},
    {"code": "NO-25", "label": "No 25 | Alien Blend", "scent": "Alien Blend", "category": "Women's Premium Oils"},
    {"code": "NO-26", "label": "No 26 | Daisy Blend", "scent": "Daisy Blend", "category": "Women's Premium Oils"},
    {"code": "NO-27", "label": "No 27 | Chanel No 5 Blend", "scent": "Chanel No 5 Blend", "category": "Women's Premium Oils"},
    {"code": "NO-28", "label": "No 28 | Delina Blend", "scent": "Delina Blend", "category": "Women's Premium Oils"},
    {"code": "NO-29", "label": "No 29 | Lost Cherry Blend", "scent": "Lost Cherry Blend", "category": "Women's Premium Oils"},
    {"code": "NO-30", "label": "No 30 | Love Don't Be Shy Blend", "scent": "Love Don't Be Shy Blend", "category": "Women's Premium Oils"},
    {"code": "NO-46", "label": "No 46 | Si Blend", "scent": "Si Blend", "category": "Women's Premium Oils"},
    {"code": "NO-47", "label": "No 47 | Bombshell Blend", "scent": "Bombshell Blend", "category": "Women's Premium Oils"},
    {"code": "NO-48", "label": "No 48 | Hypnotic Poison Blend", "scent": "Hypnotic Poison Blend", "category": "Women's Premium Oils"},
    {"code": "NO-49", "label": "No 49 | Libre Blend", "scent": "Libre Blend", "category": "Women's Premium Oils"},
    {"code": "NO-50", "label": "No 50 | Chance Eau Tendre Blend", "scent": "Chance Eau Tendre Blend", "category": "Women's Premium Oils"},
    {"code": "NO-51", "label": "No 51 | Mon Guerlain Blend", "scent": "Mon Guerlain Blend", "category": "Women's Premium Oils"},
    {"code": "NO-52", "label": "No 52 | Angel Blend", "scent": "Angel Blend", "category": "Women's Premium Oils"},
    {"code": "NO-53", "label": "No 53 | Light Blue Blend", "scent": "Light Blue Blend", "category": "Women's Premium Oils"},
    {"code": "NO-54", "label": "No 54 | Pure Poison Blend", "scent": "Pure Poison Blend", "category": "Women's Premium Oils"},
    {"code": "NO-55", "label": "No 55 | Prada Paradoxe Blend", "scent": "Prada Paradoxe Blend", "category": "Women's Premium Oils"},
    {"code": "NO-56", "label": "No 56 | Devotion Blend", "scent": "Devotion Blend", "category": "Women's Premium Oils"},
    {"code": "NO-57", "label": "No 57 | Sol de Janeiro Cheirosa 68 Blend", "scent": "Sol de Janeiro Cheirosa 68 Blend", "category": "Women's Premium Oils"},
    {"code": "NO-58", "label": "No 58 | L'Interdit Blend", "scent": "L'Interdit Blend", "category": "Women's Premium Oils"},
    {"code": "NO-59", "label": "No 59 | My Way Blend", "scent": "My Way Blend", "category": "Women's Premium Oils"},
    {"code": "NO-60", "label": "No 60 | Omnia Crystalline Blend", "scent": "Omnia Crystalline Blend", "category": "Women's Premium Oils"},
]

home_catalog = [
    {"code": "H#1", "label": "H#1 | House Blend - Laundry day", "scent": "Laundry day", "category": "Home & House Scents"},
    {"code": "H#2", "label": "H#2 | House Blend - Sunrise", "scent": "Sunrise", "category": "Home & House Scents"},
]

ALL_CATALOG_ITEMS = men_catalog + women_catalog + home_catalog
DEFAULT_INITIAL_STOCK = 5

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders_v2 (
            order_id TEXT,
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

# --- HELPER INVENTORY & CART FUNCTIONS ---
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

def calculate_order_total(quantity):
    qty = int(quantity)
    if qty <= 0:
        return 0.0, 0.0, 0.0
    
    subtotal = float(qty * 45.00)
    discount_amount = subtotal * 0.20 if subtotal > 100.00 else 0.0
    final_total = subtotal - discount_amount
    return final_total, subtotal, discount_amount

def calculate_cart_totals(cart_items):
    total_qty = sum(item["quantity"] for item in cart_items)
    subtotal = float(total_qty * 45.00)
    discount_amount = subtotal * 0.20 if subtotal > 100.00 else 0.0
    final_total = subtotal - discount_amount
    return final_total, subtotal, discount_amount, total_qty

def restock_item(product_code, add_qty):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE inventory SET stock_quantity = stock_quantity + ? WHERE product_code = ?", (add_qty, product_code))
    conn.commit()
    conn.close()

PRICE_PER_BOTTLE = 45.00
LOCAL_BOTTLE_IMG = "images/bottles.png"
LOCAL_QR_IMG = "images/zelle_qr.png"
LOCAL_CASHAPP_QR_IMG = "images/cashapp_qr.png"
LOCAL_VENMO_QR_IMG = "images/venmo_qr.png"
LOCAL_CATALOG_QR_IMG = "images/Catalog_qr.png.jpg"

# Initialize Session State Cart
if "cart_items" not in st.session_state:
    st.session_state.cart_items = []

# --- SIDEBAR ACCESS INTERFACE ---
st.sidebar.markdown("### 🔒 System Portal")
access_mode = "🛍️ Public Storefront"

with st.sidebar.expander("Staff Portal", expanded=False):
    password = st.text_input("Enter Admin Password:", type="password", key="admin_password_input")

if password == "Safe9uard-tf80":
    st.sidebar.success("Authenticated")
    access_mode = st.sidebar.radio("View Mode", ["🛍️ Public Storefront", "💼 Owner Dashboard"])
elif password:
    st.sidebar.error("Incorrect Password")

# ==========================================
# PUBLIC VIEW: ONLINE STOREFRONT
# ==========================================
if access_mode == "🛍️ Public Storefront":
    cart_count = sum(item["quantity"] for item in st.session_state.cart_items)
    cart_tab_label = f"🛒 Shopping Cart ({cart_count})"
    
    store_tab, cart_tab, track_tab = st.tabs(["🛍️ Order Online", cart_tab_label, "📦 Track My Order"])
    
    # TAB 1: PRODUCT CATALOG & ADD TO CART
    with store_tab:
        if "last_order_id" in st.session_state:
            order_id = st.session_state.last_order_id
            order_total = st.session_state.get('last_order_total', PRICE_PER_BOTTLE)
            selected_method = st.session_state.get('last_order_method', 'Zelle')
            is_preorder = st.session_state.get("last_order_preorder", 0)

            if is_preorder == 1:
                st.success(f"⭐ Priority Preorder Reserved! ID: `{order_id}`")
            else:
                st.success(f"🎉 Order Placed Successfully! ID: `{order_id}`")

            st.markdown(f"### 💰 Send Payment via **{selected_method}**:")

            if selected_method == "Zelle":
                st.info(f"Send **${order_total:.2f}** via **Zelle**:\n\n• **Recipient Phone:** `863-236-4196`\n• **Name:** Alexander Thompson\n• **Memo:** Order `{order_id}`")
                if os.path.exists(LOCAL_QR_IMG):
                    st.image(LOCAL_QR_IMG, caption="Scan with your banking app to Zelle instantly.", width=300)
            elif selected_method == "Cash App":
                st.info(f"Send **${order_total:.2f}** via **Cash App**:\n\n• **Cashtag:** `$JaMekaHowell`\n• **Name:** Jameka Howell\n• **Memo:** Order `{order_id}`")
                if os.path.exists(LOCAL_CASHAPP_QR_IMG):
                    st.image(LOCAL_CASHAPP_QR_IMG, caption="Scan with Cash App to pay instantly.", width=300)
            elif selected_method == "Venmo":
                st.info(f"Send **${order_total:.2f}** via **Venmo**:\n\n• **Username:** `@Jameka-Hatton`\n• **Name:** Jameka Hatton\n• **Memo:** Order `{order_id}`")
                if os.path.exists(LOCAL_VENMO_QR_IMG):
                    st.image(LOCAL_VENMO_QR_IMG, caption="Scan with Venmo to pay instantly.", width=300)
            else:
                st.info(f"Send **${order_total:.2f}** via **Apple Pay**:\n\n• **Send to Phone:** `863-236-4196`\n• **Note/Message:** Include Order ID `{order_id}`")

            st.warning(f"⚠️ **IMPORTANT:** Always include your Order ID **`{order_id}`** in the payment note/memo!")
            
            if st.button("Place Another Order / Clear Screen"):
                for key in ["cart_items", "web_cart", "last_order_id", "last_order_total", "last_order_method", "last_order_preorder"]:
                    st.session_state.pop(key, None)
                st.rerun()

        else:
            st.subheader("🛍️ Place Your Order Online")
            col_store_left, col_store_right = st.columns([3, 2])
            
            with col_store_left:
                with st.container(border=True):
                    st.markdown("#### 1. Select Your Fragrance")
                    cat_select = st.radio(
                        "Product Family:", 
                        ["Men's Premium Oils", "Women's Premium Oils", "Home & House Scents", "Custom / Full Catalog Request"], 
                        horizontal=True
                    )

                if cat_select == "Custom / Full Catalog Request":
                    st.info("✨ Scan the QR code or view our full master catalog, then type the fragrance name below!")
                    if os.path.exists(LOCAL_CATALOG_QR_IMG):
                        st.image(LOCAL_CATALOG_QR_IMG, caption="Scan to view Full Extended Catalog", width=250)
                    
                    custom_scent_input = st.text_input("Type Fragrance Name & Brand:")
                    matching_obj = {
                        "code": "CUSTOM-REQ",
                        "scent": custom_scent_input.strip() if custom_scent_input.strip() else "Custom Catalog Request",
                        "category": "Custom Request"
                    }
                    current_stock, initial_cap = 999, 999
                    is_preorder_item = True
                else:
                    st.markdown("#### 2. Choose Your Scent")
                    active_list = men_catalog if cat_select == "Men's Premium Oils" else (women_catalog if cat_select == "Women's Premium Oils" else home_catalog)
                    selected_display = st.selectbox("Available Inventory Index:", [item["label"] for item in active_list])
                    matching_obj = next(item for item in active_list if item["label"] == selected_display)
                    current_stock, initial_cap = get_item_stock(matching_obj["code"])
                    is_preorder_item = current_stock <= 0

                    if is_preorder_item:
                        st.info("⭐ **PRIORITY PREORDER ITEM:** Regular stock is reserved. Your order reserves a bottle in our priority batch!")
                    elif current_stock <= (initial_cap * 0.5):
                        st.warning(f"⚠️ Limited Regular Stock Remaining! (Only {current_stock} left)")
                    else:
                        st.caption(f"In Stock ({current_stock} available)")

                max_selectable = 50 if is_preorder_item else max(1, current_stock)
                web_qty = st.number_input("Quantity:", min_value=1, max_value=max_selectable, value=1, step=1)

                if os.path.exists(LOCAL_BOTTLE_IMG):
                    st.image(LOCAL_BOTTLE_IMG, use_container_width=True)

                st.markdown("---")
                if st.button("🛒 Add to Cart", type="primary", use_container_width=True):
                    existing = next((i for i in st.session_state.cart_items if i["code"] == matching_obj["code"] and i["scent"] == matching_obj["scent"]), None)
                    if existing:
                        existing["quantity"] += int(web_qty)
                    else:
                        st.session_state.cart_items.append({
                            "code": matching_obj["code"],
                            "scent": matching_obj["scent"],
                            "category": cat_select,
                            "quantity": int(web_qty),
                            "is_preorder": 1 if is_preorder_item else 0,
                            "unit_price": PRICE_PER_BOTTLE
                        })
                    st.success(f"Added {web_qty}x {matching_obj['scent']} to your cart!")
                    st.rerun()

            with col_store_right:
                st.markdown("### 🛒 Cart Quick View")
                if not st.session_state.cart_items:
                    st.info("Your shopping cart is currently empty. Add items from the catalog on the left!")
                else:
                    final_tot, sub_tot, disc_amt, total_bottles = calculate_cart_totals(st.session_state.cart_items)
                    for idx, item in enumerate(st.session_state.cart_items):
                        with st.container(border=True):
                            st.write(f"**{item['scent']}**")
                            st.write(f"• Code: `{item['code']}` | Qty: {item['quantity']}")
                            st.write(f"• Price: ${item['unit_price'] * item['quantity']:.2f}")
                            if item["is_preorder"]:
                                st.caption("⭐ Priority Preorder Item")
                    
                    st.markdown("---")
                    st.write(f"**Items:** {total_bottles} bottle(s)")
                    st.write(f"**Subtotal:** ${sub_tot:.2f}")
                    if disc_amt > 0:
                        st.success(f"🎉 **20% Bulk Savings Applied:** -${disc_amt:.2f}")
                    st.metric("Cart Subtotal", f"${final_tot:.2f}")

    # TAB 2: SHOPPING CART CHECKOUT PAGE
    with cart_tab:
        st.subheader("🛒 Shopping Cart & Checkout")
        if not st.session_state.cart_items:
            st.info("Your shopping cart is empty. Please select fragrances from the 'Order Online' tab!")
        else:
            col_cart_list, col_checkout_summary = st.columns([3, 2])
            
            with col_cart_list:
                st.markdown("#### Items in your cart")
                for idx, item in enumerate(st.session_state.cart_items):
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 2, 1])
                        with c1:
                            st.markdown(f"**{item['scent']}**")
                            st.caption(f"Category: {item['category']} | Code: {item['code']}")
                            if item["is_preorder"]:
                                st.warning("⭐ Priority Preorder Batch")
                        with c2:
                            new_qty = st.number_input(f"Qty", min_value=1, max_value=100, value=item["quantity"], key=f"cart_qty_{idx}")
                            st.session_state.cart_items[idx]["quantity"] = new_qty
                        with c3:
                            st.markdown(f"**${item['unit_price'] * item['quantity']:.2f}**")
                            if st.button("Delete", key=f"del_cart_{idx}"):
                                st.session_state.cart_items.pop(idx)
                                st.rerun()

            with col_checkout_summary:
                final_tot, sub_tot, disc_amt, total_bottles = calculate_cart_totals(st.session_state.cart_items)
                
                with st.container(border=True):
                    st.markdown("#### Shipping & Contact Info")
                    cart_cust_name = st.text_input("Full Name:", key="cart_cust_name")
                    cart_cust_phone = st.text_input("Phone Number:", key="cart_cust_phone")
                    cart_cust_address = st.text_area("Shipping Address:", key="cart_cust_address")

                    st.markdown("#### Select Settlement Channel")
                    cart_payment_method = st.selectbox(
                        "Payment Channel:",
                        ["Zelle", "Cash App", "Venmo", "Apple Pay"],
                        key="cart_payment_select"
                    )

                    st.markdown("---")
                    st.markdown("#### Order Summary")
                    st.write(f"Total Items: **{total_bottles} bottle(s)**")
                    st.write(f"Subtotal: **${sub_tot:.2f}**")
                    if disc_amt > 0:
                        st.success(f"🎉 20% Discount (> $100): **-${disc_amt:.2f}**")
                    st.markdown(f"### Total: :green[${final_tot:.2f}]")

                    has_preorder = any(i["is_preorder"] == 1 for i in st.session_state.cart_items)
                    place_btn_label = "Place Priority Preorder" if has_preorder else "Place Your Order"

                    if st.button(place_btn_label, type="primary", use_container_width=True):
                        if not cart_cust_name.strip() or not cart_cust_phone.strip() or not cart_cust_address.strip():
                            st.error("⚠️ Please complete your Name, Phone Number, and Delivery Address.")
                        else:
                            generated_id = f"TF-WEB-{int(time.time())}"
                            timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            conn = get_db_connection()
                            cursor = conn.cursor()

                            for item in st.session_state.cart_items:
                                item_total, _, _ = calculate_order_total(item["quantity"])
                                initial_status = "Preorder - Awaiting Batch Restock" if item["is_preorder"] == 1 else "Awaiting Settlement"

                                cursor.execute("""
                                    INSERT INTO orders_v2 
                                    (order_id, timestamp, customer_name, phone_number, delivery_address, category, product_code, scent_name, quantity, total_paid, payment_method, is_preorder, status, order_type)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    generated_id, timestamp_str, cart_cust_name.strip(), cart_cust_phone.strip(), cart_cust_address.strip(), 
                                    item['category'], item['code'], item['scent'], item['quantity'], item_total, 
                                    cart_payment_method, item['is_preorder'], initial_status, 'Online Store'
                                ))

                                if item["is_preorder"] == 0:
                                    deduct_inventory(item['code'], item['quantity'])

                            conn.commit()
                            conn.close()

                            st.session_state.last_order_id = generated_id
                            st.session_state.last_order_total = final_tot
                            st.session_state.last_order_method = cart_payment_method
                            st.session_state.last_order_preorder = 1 if has_preorder else 0
                            
                            st.session_state.cart_items = []
                            st.rerun()

    # TAB 3: ORDER TRACKING
    with track_tab:
        st.subheader("📦 Real-Time Order Tracking")
        cust_query_input = st.text_input("Order ID or Phone Number:", placeholder="TF-WEB-1234 or 863-555-0199", key="customer_track_input").strip()
        
        if st.button("Track Order", type="primary"):
            if cust_query_input:
                try:
                    conn = get_db_connection()
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
                        st.markdown(f"### Found {len(rows)} Matching Item(s)")
                        grouped_orders = {}
                        for r in rows:
                            oid = r["order_id"]
                            if oid not in grouped_orders:
                                grouped_orders[oid] = []
                            grouped_orders[oid].append(r)

                        for oid, items in grouped_orders.items():
                            with st.container(border=True):
                                first_item = items[0]
                                status_raw = first_item["status"]
                                status_emoji = "⭐" if "Preorder" in status_raw else ("📦" if "Paid" in status_raw else ("✅" if "Completed" in status_raw else "⏳"))
                                status_color = "blue" if "Preorder" in status_raw or "Paid" in status_raw else ("green" if "Completed" in status_raw else "orange")
                                    
                                st.markdown(f"### Order ID: `{oid}`")
                                st.markdown(f"#### Status: :{status_color}[{status_emoji} {status_raw}]")
                                
                                col_details_1, col_details_2 = st.columns(2)
                                with col_details_1:
                                    st.write(f"• **Customer:** {first_item['customer_name']}")
                                    st.write(f"• **Phone:** {first_item['phone_number']}")
                                    st.write(f"• **Order Date:** {first_item['timestamp']}")
                                with col_details_2:
                                    st.write(f"• **Settlement Channel:** {first_item['payment_method']}")
                                    st.write(f"• **Shipping Address:** {first_item['delivery_address']}")

                                st.markdown("**Purchased Items:**")
                                for itm in items:
                                    st.write(f"• {itm['scent_name']} ({itm['quantity']} bottle(s)) - ${itm['total_paid']:.2f}")
                    else:
                        st.error("No orders found matching that Order ID or Phone Number.")
                except Exception as e:
                    st.error(f"Error querying database: {e}")
            else:
                st.warning("Please enter an Order ID or Phone Number.")

# ==========================================
# PRIVATE VIEW: OWNER HUB & POS
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
                    generated_id = f"TF-POS-{random.randint(1000, 9999)}"
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
                restock_item(target_code, int(add_amount))
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
        user_query_input = st.text_input("Input Order Code or Customer Phone Number:", placeholder="TF-WEB-1234").strip()
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

# --- GLOBAL FOOTER ---
st.markdown("---")
st.markdown("<div style='font-size: 0.8rem; color: #64748B;'><strong>LEGAL DISCLAIMER:</strong> T Fragrances products are independent creations and are not affiliated with, sponsored by, or endorsed by original designer brands. Reference names are strictly for scent classification.</div>", unsafe_allow_html=True)
