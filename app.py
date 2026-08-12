import streamlit as st
import sqlite3
import datetime
import time
import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# --- PAGE SETUP & AMAZON-STYLE THEMING ---
st.set_page_config(page_title="T Fragrances | Luxury Oils & Scents", page_icon="✨", layout="wide")

# Custom Styling for E-Commerce Look
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F1111;
        text-align: center;
        letter-spacing: 1px;
    }
    .sub-header {
        text-align: center;
        color: #565959;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    .price-tag {
        font-size: 1.4rem;
        font-weight: bold;
        color: #B12704;
    }
    .product-card {
        border: 1px solid #E7E7E7;
        border-radius: 8px;
        padding: 15px;
        background-color: #FFFFFF;
        margin-bottom: 15px;
    }
    .badge-in-stock {
        color: #007600;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .badge-preorder {
        color: #C45500;
        font-weight: bold;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- MASTER CATALOG DATA ---
MEN_CATALOG = [
    {"code": "NO-1", "label": "No 1 | No 1 Sauvage Blend", "scent": "No 1 Sauvage Blend", "category": "Men's Cologne Oils", "price": 45.00, "desc": "Fresh, spicy, and woody 100% pure oil blend inspired by Sauvage."},
    {"code": "NO-4", "label": "No 4 | No 4 Aventus Blend", "scent": "No 4 Aventus Blend", "category": "Men's Cologne Oils", "price": 45.00, "desc": "Rich, smoky pineapple and birch signature blend."},
    {"code": "NO-5", "label": "No 5 | Bleu Elegance Blend", "scent": "Bleu Elegance Blend", "category": "Men's Cologne Oils", "price": 45.00, "desc": "Aromatic citrus paired with deep cedar and sandalwood."},
]

WOMEN_CATALOG = [
    {"code": "NO-2", "label": "No 2 | No 2 Good Girl Blend", "scent": "No 2 Good Girl Blend", "category": "Women's Perfume Oils", "price": 45.00, "desc": "Sweet jasmine, cocoa, and tonka bean elegant blend."},
    {"code": "NO-3", "label": "No 3 | No 3 Rouge 540 Blend", "scent": "No 3 Rouge 540 Blend", "category": "Women's Perfume Oils", "price": 45.00, "desc": "Luminous saffron, amberwood, and fir resin luxurious oil."},
    {"code": "NO-6", "label": "No 6 | Flowerbomb Luxury Blend", "scent": "Flowerbomb Luxury Blend", "category": "Women's Perfume Oils", "price": 45.00, "desc": "Explosive floral bouquet of patchouli, freesia, and rose."},
]

HOME_CATALOG = [
    {"code": "H#1", "label": "H#1 | House Blend - Laundry Day", "scent": "Laundry Day", "category": "Home Scents", "price": 45.00, "desc": "Crisp, clean linen notes engineered to refresh any room."},
    {"code": "H#2", "label": "H#2 | House Blend - Sunrise", "scent": "Sunrise", "category": "Home Scents", "price": 45.00, "desc": "Bright citrus notes blended with warm morning amber."},
    {"code": "H#3", "label": "H#3 | House Blend - Velvet Oud", "scent": "Velvet Oud", "category": "Home Scents", "price": 45.00, "desc": "Deep, cozy atmospheric blend featuring subtle vanilla and oud."},
]

ALL_CATALOG = MEN_CATALOG + WOMEN_CATALOG + HOME_CATALOG
DEFAULT_STOCK = 5
DB_FILE = "t_fragrances_store.db"

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_code TEXT PRIMARY KEY,
            category TEXT,
            scent_name TEXT,
            price REAL,
            stock_quantity INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            timestamp TEXT,
            customer_name TEXT,
            phone_number TEXT,
            address TEXT,
            items_json TEXT,
            total_amount REAL,
            payment_method TEXT,
            status TEXT
        )
    """)
    for item in ALL_CATALOG:
        cursor.execute("""
            INSERT OR IGNORE INTO inventory (product_code, category, scent_name, price, stock_quantity)
            VALUES (?, ?, ?, ?, ?)
        """, (item["code"], item["category"], item["scent"], item["price"], DEFAULT_STOCK))
    conn.commit()
    conn.close()

init_db()

def get_stock(code):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT stock_quantity FROM inventory WHERE product_code = ?", (code,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else DEFAULT_STOCK

# --- DYNAMIC 50ML BOTTLE IMAGE GENERATOR ---
def create_clear_bottle_image(scent_name, category):
    """Generates a dynamic 50ml clear glass bottle render with T Fragrances branding."""
    img = Image.new("RGBA", (300, 380), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Cap (Metallic Silver)
    draw.rectangle([115, 30, 185, 80], fill=(200, 200, 205, 255), outline=(140, 140, 145, 255), width=2)
    draw.rectangle([125, 80, 175, 95], fill=(170, 170, 175, 255))
    
    # Bottle Liquid Tint by Category
    tint = (245, 230, 200, 110) if "Men" in category else ((255, 220, 230, 110) if "Women" in category else (220, 240, 255, 110))
    
    # Glass Body Outline & Liquid Fill
    draw.rounded_rectangle([75, 95, 225, 330], radius=15, fill=tint, outline=(180, 180, 185, 220), width=3)
    
    # Highlight reflection for transparent glass effect
    draw.line([85, 105, 85, 315], fill=(255, 255, 255, 180), width=4)
    
    # Bottle Label Container
    draw.rectangle([92, 160, 208, 270], fill=(255, 255, 255, 240), outline=(30, 41, 59, 255), width=2)
    
    # Brand Label Text
    draw.text((150, 175), "T FRAGRANCES", fill=(15, 23, 42, 255), anchor="mm")
    draw.line([105, 192, 195, 192], fill=(15, 23, 42, 255), width=1)
    
    # Scent Title Wrap
    short_scent = scent_name[:18] + "..." if len(scent_name) > 18 else scent_name
    draw.text((150, 210), short_scent, fill=(51, 65, 85, 255), anchor="mm")
    draw.text((150, 232), "50ml e 1.7 fl.oz", fill=(100, 116, 139, 255), anchor="mm")
    draw.text((150, 250), "100% PURE OIL", fill=(185, 28, 28, 255), anchor="mm")
    
    return img

# --- SESSION STATE (CART) INITIALIZATION ---
if "cart" not in st.session_state:
    st.session_state.cart = {}

# --- HEADER & NAVIGATION BAR ---
st.markdown("<div class='main-header'>T FRAGRANCES</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Designer Quality (50ml) | 100% Pure Oil-Based | Reimagined Luxury</div>", unsafe_allow_html=True)

total_cart_items = sum(item["qty"] for item in st.session_state.cart.values())

col_nav_1, col_nav_2 = st.columns([4, 1])
with col_nav_1:
    search_term = st.text_input("🔍 Search colognes, perfumes, or house scents...", placeholder="Type Sauvage, Rouge 540, Laundry Day...", label_visibility="collapsed")
with col_nav_2:
    st.button(f"🛒 Cart ({total_cart_items})", type="primary", use_container_width=True, key="view_cart_btn")

st.markdown("---")

# --- MAIN LAYOUT (STORE & CART SIDEBAR) ---
main_col, cart_col = st.columns([3, 1.2])

with main_col:
    # Filter Tabs
    tab_all, tab_men, tab_women, tab_home = st.tabs(["✨ All Scents", "👔 Men's Colognes", "👗 Women's Perfumes", "🏠 House Blends"])
    
    def render_catalog_grid(items_list):
        # Filter search query
        filtered = [
            i for i in items_list 
            if search_term.lower() in i["scent"].lower() 
            or search_term.lower() in i["category"].lower()
            or search_term.lower() in i["code"].lower()
        ]
        
        if not filtered:
            st.info("No fragrances found matching your search.")
            return

        # Render 2 products per row
        for idx in range(0, len(filtered), 2):
            cols = st.columns(2)
            for c_idx, item in enumerate(filtered[idx:idx+2]):
                stock = get_stock(item["code"])
                bottle_img = create_clear_bottle_image(item["scent"], item["category"])
                
                with cols[c_idx]:
                    with st.container(border=True):
                        st.image(bottle_img, use_container_width=True)
                        st.markdown(f"#### {item['scent']}")
                        st.caption(f"Code: `{item['code']}` | Category: {item['category']}")
                        st.write(item["desc"])
                        st.markdown(f"<div class='price-tag'>${item['price']:.2f}</div>", unsafe_allow_html=True)
                        
                        if stock > 0:
                            st.markdown(f"<span class='badge-in-stock'>In Stock ({stock} available)</span>", unsafe_allow_html=True)
                        else:
                            st.markdown("<span class='badge-preorder'>⭐ Preorder (Priority Batch)</span>", unsafe_allow_html=True)
                        
                        col_qty, col_add = st.columns([1, 2])
                        with col_qty:
                            qty_input = st.number_input("Qty", min_value=1, max_value=max(1, stock if stock > 0 else 20), value=1, key=f"qty_{item['code']}")
                        with col_add:
                            st.write("") # Alignment spacing
                            if st.button("Add to Cart 🛒", key=f"add_{item['code']}", use_container_width=True):
                                code = item["code"]
                                if code in st.session_state.cart:
                                    st.session_state.cart[code]["qty"] += qty_input
                                else:
                                    st.session_state.cart[code] = {
                                        "scent": item["scent"],
                                        "price": item["price"],
                                        "qty": qty_input,
                                        "code": code,
                                        "category": item["category"]
                                    }
                                st.toast(f"Added {qty_input}x {item['scent']} to cart!", icon="🛒")
                                time.sleep(0.3)
                                st.rerun()

    with tab_all:
        render_catalog_grid(ALL_CATALOG)
    with tab_men:
        render_catalog_grid(MEN_CATALOG)
    with tab_women:
        render_catalog_grid(WOMEN_CATALOG)
    with tab_home:
        render_catalog_grid(HOME_CATALOG)

# --- SHOPPING CART SIDEBAR PANEL ---
with cart_col:
    with st.container(border=True):
        st.subheader("🛒 Shopping Cart Summary")
        
        if not st.session_state.cart:
            st.info("Your shopping cart is currently empty.")
        else:
            subtotal = 0.0
            items_to_remove = []
            
            for code, details in st.session_state.cart.items():
                item_total = details["price"] * details["qty"]
                subtotal += item_total
                
                st.markdown(f"**{details['scent']}**")
                c_c1, c_c2, c_c3 = st.columns([2, 2, 1])
                with c_c1:
                    st.caption(f"${details['price']:.2f} x {details['qty']}")
                with c_c2:
                    st.write(f"**${item_total:.2f}**")
                with c_c3:
                    if st.button("❌", key=f"del_{code}"):
                        items_to_remove.append(code)
                st.markdown("---")
            
            for code in items_to_remove:
                del st.session_state.cart[code]
                st.rerun()
                
            # Volume Discount Calculation (> $100 gets 20% off)
            discount = subtotal * 0.20 if subtotal > 100.00 else 0.0
            final_total = subtotal - discount
            
            st.write(f"Subtotal: **${subtotal:.2f}**")
            if discount > 0:
                st.success(f"20% Order Discount: **-${discount:.2f}**")
            st.markdown(f"### Total: **${final_total:.2f}**")
            
            st.markdown("---")
            st.markdown("### 📦 Delivery Details")
            c_name = st.text_input("Full Name:", key="cart_name")
            c_phone = st.text_input("Phone Number:", key="cart_phone")
            c_address = st.text_area("Shipping Address:", key="cart_address")
            c_payment = st.selectbox("Payment Channel:", ["Zelle", "Cash App", "Venmo", "Apple Pay"])
            
            if st.button("Proceed to Place Order", type="primary", use_container_width=True):
                if not c_name.strip() or not c_phone.strip() or not c_address.strip():
                    st.error("Please fill out your name, phone, and address.")
                else:
                    order_id = f"TF-AMZ-{int(time.time())}"
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Deduct stock and commit order
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    
                    for code, item in st.session_state.cart.items():
                        cursor.execute("UPDATE inventory SET stock_quantity = MAX(0, stock_quantity - ?) WHERE product_code = ?", (item["qty"], code))
                        
                    cursor.execute("""
                        INSERT INTO orders (order_id, timestamp, customer_name, phone_number, address, items_json, total_amount, payment_method, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (order_id, timestamp, c_name, c_phone, c_address, str(st.session_state.cart), final_total, c_payment, "Awaiting Payment"))
                    
                    conn.commit()
                    conn.close()
                    
                    st.session_state.last_placed_order = {
                        "id": order_id,
                        "total": final_total,
                        "method": c_payment
                    }
                    st.session_state.cart = {}
                    st.rerun()

# --- ORDER CONFIRMATION MODAL ---
if "last_placed_order" in st.session_state:
    order_info = st.session_state.last_placed_order
    st.balloons()
    st.success(f"🎉 Order Placed Successfully! Your Order ID is **`{order_info['id']}`**")
    
    with st.expander("💳 Complete Payment Instructions", expanded=True):
        method = order_info["method"]
        tot = order_info["total"]
        oid = order_info["id"]
        
        st.markdown(f"#### Send Total Payment: **${tot:.2f}** via **{method}**")
        
        if method == "Cash App":
            st.info(f"• **Cashtag:** `$JaMekaHowell`\n• **Name:** Jameka Howell\n• **Memo:** Order `{oid}`")
            if os.path.exists("images/cashapp_qr.png"):
                st.image("images/cashapp_qr.png", width=250)
        elif method == "Venmo":
            st.info(f"• **Username:** `@Jameka-Hatton`\n• **Name:** Jameka Hatton\n• **Memo:** Order `{oid}`")
            if os.path.exists("images/venmo_qr.png"):
                st.image("images/venmo_qr.png", width=250)
        elif method == "Zelle":
            st.info(f"• **Phone:** `863-236-4196`\n• **Name:** Alexander Thompson\n• **Memo:** Order `{oid}`")
            if os.path.exists("images/zelle_qr.png"):
                st.image("images/zelle_qr.png", width=250)
        else:
            st.info(f"• **Send Apple Pay to:** `863-236-4196`\n• **Note:** Include Order ID `{oid}`")
            
        st.warning("⚠️ **IMPORTANT:** Always put your Order ID in the payment memo field!")
        
    if st.button("Continue Shopping"):
        del st.session_state.last_placed_order
        st.rerun()

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #565959; font-size: 0.8rem;'>© T Fragrances Storefront. High-Performance Fragrance Oils in 50ml Clear Bottles.</p>", unsafe_allow_html=True)
