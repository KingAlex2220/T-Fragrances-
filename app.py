import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="T Fragrances | Storefront & POS",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# DATABASE SETUP & INITIALIZATION
# ==========================================
DB_FILE = "t_fragrances.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Create Orders Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT,
            customer_name TEXT,
            customer_email TEXT,
            customer_phone TEXT,
            shipping_address TEXT,
            items_summary TEXT,
            total_qty INTEGER,
            subtotal REAL,
            discount_applied REAL,
            final_total REAL,
            payment_method TEXT,
            status TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_order_to_db(name, email, phone, address, items_summary, qty, subtotal, discount, total, payment_method, notes):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO orders (
            order_date, customer_name, customer_email, customer_phone, 
            shipping_address, items_summary, total_qty, subtotal, 
            discount_applied, final_total, payment_method, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (order_date, name, email, phone, address, items_summary, qty, subtotal, discount, total, payment_method, "Pending Payment", notes))
    conn.commit()
    conn.close()

def get_all_orders():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
    conn.close()
    return df

def update_order_status(order_id, new_status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

# ==========================================
# GLOBAL DISCLAIMER & CATALOG DATA
# ==========================================
DISCLAIMER_TEXT = (
    "TF Fragrances offers proprietary, independently formulated scents inspired by popular fragrance profiles. "
    "Any reference to scent families or style impressions is strictly for descriptive purposes to give customers "
    "an idea of the olfactory notes. TF Fragrances does not use third-party trademarked names, nor are our products "
    "affiliated with, endorsed by, or sponsored by any third-party brands or manufacturers."
)

FRAGRANCE_CATALOG = [
    # --- MEN'S COLLECTION (30) ---
    {"id": "m01", "name": "Savage Spirit", "gender": "Men", "category": "Fresh & Spicy", "price": 45.0, "notes": "Inspired by Sauvage profile — Crisp bergamot, pepper, and rich ambroxan."},
    {"id": "m02", "name": "Monarch Creed", "gender": "Men", "category": "Fruity & Woody", "price": 45.0, "notes": "Inspired by Aventus profile — Smoky pineapple, birchwood, and oakmoss."},
    {"id": "m03", "name": "Azure Night", "gender": "Men", "category": "Woody & Aromatic", "price": 45.0, "notes": "Inspired by Bleu de Chanel profile — Fresh grapefruit, incense, and cedarwood."},
    {"id": "m04", "name": "Oceanic Drift", "gender": "Men", "category": "Aquatic & Fresh", "price": 45.0, "notes": "Inspired by Acqua Di Gio profile — Marine minerals, mandarin, and ocean breeze."},
    {"id": "m05", "name": "Smoky Reserve", "gender": "Men", "category": "Warm & Gourmand", "price": 45.0, "notes": "Inspired by Tobacco Vanille profile — Rich tobacco leaf, sweet vanilla, and spices."},
    {"id": "m06", "name": "Sailor's Pride", "gender": "Men", "category": "Oriental & Fresh", "price": 45.0, "notes": "Inspired by Le Male profile — Classic mint, lavender, and warm tonka bean."},
    {"id": "m07", "name": "Crimson Rush", "gender": "Men", "category": "Spicy & Woody", "price": 45.0, "notes": "Inspired by Spicebomb profile — Fiery red saffron, fresh grapefruit, and redwood."},
    {"id": "m08", "name": "Gilded Leather", "gender": "Men", "category": "Woody Leather", "price": 45.0, "notes": "Inspired by Tuscan Leather profile — Warm lavender, Italian lemon, and cedarwood."},
    {"id": "m09", "name": "Metallic Citrus", "gender": "Men", "category": "Fresh Citrus", "price": 45.0, "notes": "Inspired by Chrome Legend profile — Crisp green apple, bergamot, and warm amber."},
    {"id": "m10", "name": "Empire Night", "gender": "Men", "category": "Aromatic Spice", "price": 45.0, "notes": "Inspired by Playboy New York profile — Fresh lime, crushed black pepper, and tonka."},
    {"id": "m11", "name": "Capital Gold", "gender": "Men", "category": "Sweet Spice", "price": 45.0, "notes": "Inspired by 1 Million profile — Blood mandarin, cinnamon, and warm leather."},
    {"id": "m12", "name": "Eternity Code", "gender": "Men", "category": "Oriental Woody", "price": 45.0, "notes": "Inspired by Armani Code profile — Lemon zest, star anise, and smooth leather."},
    {"id": "m13", "name": "Velvet Oud", "gender": "Men", "category": "Woody Oriental", "price": 45.0, "notes": "Inspired by Oud Wood profile — Rare oudwood, sandalwood, and Sichuan pepper."},
    {"id": "m14", "name": "Invincible Sport", "gender": "Men", "category": "Fresh Marine", "price": 45.0, "notes": "Inspired by Invictus profile — Grapefruit, sea salt, and bay leaf accord."},
    {"id": "m15", "name": "Night Hero", "gender": "Men", "category": "Ambery Spice", "price": 45.0, "notes": "Inspired by Wanted by Night profile — Bergamot, roasted coffee, and vetiver base."},
    {"id": "m16", "name": "Urban Legend", "gender": "Men", "category": "Woody Aquatic", "price": 45.0, "notes": "Inspired by Light Blue Pour Homme profile — Sea salt, sage, and driftwood notes."},
    {"id": "m17", "name": "Bourbon Spice", "gender": "Men", "category": "Warm Gourmand", "price": 45.0, "notes": "Inspired by Angels' Share profile — Aged whiskey, cinnamon bark, and dark amber."},
    {"id": "m18", "name": "Midnight Nomad", "gender": "Men", "category": "Oriental Spice", "price": 45.0, "notes": "Inspired by Ombre Leather profile — Cardamom, leather, and smoked amber."},
    {"id": "m19", "name": "Royal Vetiver", "gender": "Men", "category": "Earthy Woody", "price": 45.0, "notes": "Inspired by Terre d'Hermes profile — Haitian vetiver, grapefruit, and pink pepper."},
    {"id": "m20", "name": "Silver Mountain", "gender": "Men", "category": "Fresh Green", "price": 45.0, "notes": "Inspired by Silver Mountain Water profile — Green tea, blackcurrant, and sandalwood."},
    {"id": "m21", "name": "Black Amber", "gender": "Men", "category": "Dark Woody", "price": 45.0, "notes": "Inspired by Black Orchid profile — Rich amber, patchouli, and dark cocoa."},
    {"id": "m22", "name": "Citrus Grove", "gender": "Men", "category": "Fresh Citrus", "price": 45.0, "notes": "Inspired by Neroli Portofino profile — Sicilian lemon, neroli, and cedar."},
    {"id": "m23", "name": "Desert Sage", "gender": "Men", "category": "Aromatic Herbal", "price": 45.0, "notes": "Inspired by Y Le Parfum profile — Wild sage, lavender, and dried cedar wood."},
    {"id": "m24", "name": "Vanguard Oud", "gender": "Men", "category": "Spicy Oud", "price": 45.0, "notes": "Inspired by Royal Oud profile — Dark leather, cardamom, and smoky agarwood."},
    {"id": "m25", "name": "Iron & Oak", "gender": "Men", "category": "Earthy & Woody", "price": 45.0, "notes": "Inspired by Legend profile — Oakmoss, clean cedar, and bergamot."},
    {"id": "m26", "name": "Aromatic Noir", "gender": "Men", "category": "Woody Floral", "price": 45.0, "notes": "Inspired by Dior Homme Intense profile — Iris, cardamom, and sandalwood blend."},
    {"id": "m27", "name": "Pacific Breeze", "gender": "Men", "category": "Clean Aquatic", "price": 45.0, "notes": "Inspired by Aqva Pour Homme profile — Ocean salt, melon, and light musk."},
    {"id": "m28", "name": "Titanium Sport", "gender": "Men", "category": "Fresh Citrus", "price": 45.0, "notes": "Inspired by Allure Homme Sport profile — Mandarin, pepper, and white musk."},
    {"id": "m29", "name": "Equestrian Red", "gender": "Men", "category": "Fruity Spice", "price": 45.0, "notes": "Inspired by Polo Red profile — Red apple, saffron, and coffee accord."},
    {"id": "m30", "name": "Solitude", "gender": "Men", "category": "Minimalist Wood", "price": 45.0, "notes": "Inspired by Molecule 01 profile — Iso E Super, cedar, and subtle amber notes."},

    # --- WOMEN'S COLLECTION (30) ---
    {"id": "w01", "name": "Crystal Rouge 540", "gender": "Women", "category": "Amber & Floral", "price": 45.0, "notes": "Inspired by Baccarat Rouge 540 profile — Jasmine, saffron, cedarwood, and ambergris."},
    {"id": "w02", "name": "Midnight Vanilla", "gender": "Women", "category": "Warm Gourmand", "price": 45.0, "notes": "Inspired by Black Opium profile — Rich black coffee, white flowers, and sweet vanilla."},
    {"id": "w03", "name": "Stiletto Velvet", "gender": "Women", "category": "Sweet Floral", "price": 45.0, "notes": "Inspired by Good Girl profile — Tuberose, roasted tonka bean, and cocoa."},
    {"id": "w04", "name": "Heavenly Dream", "gender": "Women", "category": "Gourmand Floral", "price": 45.0, "notes": "Inspired by Cloud profile — Coconut cream, lavender, and praline sweet musk."},
    {"id": "w05", "name": "Golden Blossom", "gender": "Women", "category": "Classic Floral", "price": 45.0, "notes": "Inspired by J'adore profile — Ylang-ylang, Damask rose, and jasmine."},
    {"id": "w06", "name": "Royal Peony", "gender": "Women", "category": "Soft Floral", "price": 45.0, "notes": "Inspired by Delina profile — Lychee, Turkish rose, peony, and vanilla."},
    {"id": "w07", "name": "Sweet Cherry Nectar", "gender": "Women", "category": "Fruity Gourmand", "price": 45.0, "notes": "Inspired by Lost Cherry profile — Black cherry, bitter almond, and liquor notes."},
    {"id": "w08", "name": "Empress Bloom", "gender": "Women", "category": "Fresh Floral", "price": 45.0, "notes": "Inspired by Chance Eau Tendre profile — Pink pepper, jasmine sambac, and white musk."},
    {"id": "w09", "name": "Nectarine Sunset", "gender": "Women", "category": "Fruity Floral", "price": 45.0, "notes": "Inspired by Nectarine Blossom & Honey profile — Sweet nectarine, peach, and plum blossom."},
    {"id": "w10", "name": "Gilded Vanilla", "gender": "Women", "category": "Warm Amber", "price": 45.0, "notes": "Inspired by Vanilla Sex profile — Madagascar vanilla, orchid, and warm amber."},
    {"id": "w11", "name": "Opulent Orchid", "gender": "Women", "category": "Exotic Floral", "price": 45.0, "notes": "Inspired by Velvet Orchid profile — Black orchid, rum, and velvety spices."},
    {"id": "w12", "name": "Satin Iris", "gender": "Women", "category": "Powdery Floral", "price": 45.0, "notes": "Inspired by Iris Poudre profile — Florentine iris, violet leaves, and soft suede."},
    {"id": "w13", "name": "Citrus Bloom", "gender": "Women", "category": "Fresh Citrus", "price": 45.0, "notes": "Inspired by Coco Mademoiselle profile — Orange blossom, neroli, and bergamot peel."},
    {"id": "w14", "name": "Velvet Rose", "gender": "Women", "category": "Deep Floral", "price": 45.0, "notes": "Inspired by Velvet Rose & Oud profile — Clove, Damask rose, and smoky oud wood."},
    {"id": "w15", "name": "Solar Jasmine", "gender": "Women", "category": "Bright Floral", "price": 45.0, "notes": "Inspired by Alien profile — Solar jasmine, cashmere wood, and white amber."},
    {"id": "w16", "name": "Blush Bouquet", "gender": "Women", "category": "Soft Floral", "price": 45.0, "notes": "Inspired by Miss Dior profile — Peony, green mandarin, and white musk."},
    {"id": "w17", "name": "Sugar Petals", "gender": "Women", "category": "Sweet Gourmand", "price": 45.0, "notes": "Inspired by Sweet Like Candy profile — Spun sugar, red berries, and whipped cream."},
    {"id": "w18", "name": "Amber Seduction", "gender": "Women", "category": "Warm Spice", "price": 45.0, "notes": "Inspired by Amber Rouge profile — Amber resins, plum, and warm cinnamon."},
    {"id": "w19", "name": "Island Coconut", "gender": "Women", "category": "Tropical Fresh", "price": 45.0, "notes": "Inspired by Bronze Goddess profile — Toasted coconut, tiare flower, and vanilla bean."},
    {"id": "w20", "name": "Radiant Goddess", "gender": "Women", "category": "Oriental Floral", "price": 45.0, "notes": "Inspired by Olympea profile — Salty vanilla, water jasmine, and ginger lily."},
    {"id": "w21", "name": "Cozy Cashmere", "gender": "Women", "category": "Warm & Cozy", "price": 45.0, "notes": "Inspired by Warm Cashmere profile — Soft cashmere, sandalwood, and white amber."},
    {"id": "w22", "name": "Pink Freesia", "gender": "Women", "category": "Fresh Floral", "price": 45.0, "notes": "Inspired by English Pear & Freesia profile — King William pear, white freesia, and patchouli."},
    {"id": "w23", "name": "Luminous Pearl", "gender": "Women", "category": "Clean Floral", "price": 45.0, "notes": "Inspired by Pure Poison profile — White lily, bergamot, and sheer musk."},
    {"id": "w24", "name": "Caramel Mist", "gender": "Women", "category": "Sweet Gourmand", "price": 45.0, "notes": "Inspired by Cheirosa 62 profile — Warm caramel, salted butter, and vanilla."},
    {"id": "w25", "name": "Botanical Garden", "gender": "Women", "category": "Green Floral", "price": 45.0, "notes": "Inspired by Gucci Bloom profile — Tuberose, jasmine, and Rangoon creeper."},
    {"id": "w26", "name": "Midnight Rose", "gender": "Women", "category": "Fruity Floral", "price": 45.0, "notes": "Inspired by Tresor Midnight Rose profile — Raspberry, rose absolute, and vanilla spice."},
    {"id": "w27", "name": "Golden Aura", "gender": "Women", "category": "Warm Amber", "price": 45.0, "notes": "Inspired by Grand Soir profile — Honey, benzoin resin, and rich amber."},
    {"id": "w28", "name": "Wild Blackberry", "gender": "Women", "category": "Fruity Woody", "price": 45.0, "notes": "Inspired by Blackberry & Bay profile — Blackberry juice, bay leaves, and cedarwood."},
    {"id": "w29", "name": "Heavenly Musk", "gender": "Women", "category": "Clean Skin Musk", "price": 45.0, "notes": "Inspired by Glossier You profile — White musk, iris, and subtle cotton notes."},
    {"id": "w30", "name": "Elysian Breeze", "gender": "Women", "category": "Fresh Aquatic", "price": 45.0, "notes": "Inspired by L'Imperatrice profile — Water mint, water lily, and cedar."}
]

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "cart" not in st.session_state:
    st.session_state.cart = {}

def add_to_cart(item_id):
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id] += 1
    else:
        st.session_state.cart[item_id] = 1
    st.toast("Added to bag!", icon="🛍️")

# ==========================================
# SIDEBAR NAVIGATION & CART SUMMARY
# ==========================================
st.sidebar.title("✨ T Fragrances")
st.sidebar.caption("50ml Clear Bottle Luxury Impressions")

search_term = st.sidebar.text_input("🔍 Search fragrances...", "").lower()
selected_gender = st.sidebar.radio("Collection", ["All", "Men", "Women"])

st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Your Shopping Bag")

total_qty = sum(st.session_state.cart.values())
raw_subtotal = sum(
    next(item["price"] for item in FRAGRANCE_CATALOG if item["id"] == i_id) * qty
    for i_id, qty in st.session_state.cart.items()
)

# Bulk Pricing Calculation
discount = 0.0
if total_qty >= 3:
    discount = 0.15  # 15% off for 3 or more
elif total_qty == 2:
    discount = 0.10  # 10% off for 2

final_subtotal = raw_subtotal * (1 - discount)

st.sidebar.write(f"**Items in Bag:** {total_qty}")
if discount > 0:
    st.sidebar.write(f"**Bulk Discount:** {int(discount * 100)}% OFF")
    st.sidebar.write(f"~~Original: ${raw_subtotal:.2f}~~")
st.sidebar.subheader(f"Total: ${final_subtotal:.2f}")

# ==========================================
# MAIN CONTENT AREA
# ==========================================
st.title("T Fragrances Storefront & POS")
st.write("Hand-crafted, long-lasting 50ml fragrance oils.")

with st.expander("ℹ️ Read Legal & Brand Notice"):
    st.write(DISCLAIMER_TEXT)

# Filter Data
filtered_catalog = FRAGRANCE_CATALOG
if selected_gender != "All":
    filtered_catalog = [x for x in filtered_catalog if x["gender"] == selected_gender]

if search_term:
    filtered_catalog = [
        x for x in filtered_catalog 
        if search_term in x["name"].lower() or search_term in x["notes"].lower() or search_term in x["category"].lower()
    ]

# Navigation Tabs
tabs = st.tabs(["🛍️ Browse Catalog", "🛒 Checkout & Order", "🔒 Admin Dashboard"])

# TAB 1: BROWSE CATALOG
with tabs[0]:
    st.caption(f"Showing {len(filtered_catalog)} scents")
    
    cols = st.columns(3)
    for idx, item in enumerate(filtered_catalog):
        col = cols[idx % 3]
        with col:
            with st.container(border=True):
                st.markdown(f"### {item['name']}")
                st.caption(f"**{item['gender']}'s** • {item['category']}")
                st.write(f"*{item['notes']}*")
                st.subheader(f"${item['price']:.2f}")
                
                st.button(
                    "Add to Bag", 
                    key=f"btn_{item['id']}", 
                    on_click=add_to_cart, 
                    args=(item['id'],)
                )

# TAB 2: CHECKOUT & ORDER (POS INTEGRATION)
with tabs[1]:
    st.header("Order Checkout")
    
    if not st.session_state.cart:
        st.info("Your shopping bag is currently empty.")
    else:
        st.subheader("Selected Items")
        cart_data = []
        summary_list = []
        
        for item_id, qty in st.session_state.cart.items():
            product = next(p for p in FRAGRANCE_CATALOG if p["id"] == item_id)
            cart_data.append({
                "Product Name": product["name"],
                "Category": product["category"],
                "Qty": qty,
                "Price": f"${product['price']:.2f}",
                "Total": f"${product['price'] * qty:.2f}"
            })
            summary_list.append(f"{qty}x {product['name']}")
        
        st.table(pd.DataFrame(cart_data))
        
        col_summary_1, col_summary_2 = st.columns(2)
        with col_summary_1:
            st.markdown(f"**Total Items:** {total_qty}")
            st.markdown(f"**Applied Discount:** {int(discount * 100)}%")
            st.markdown(f"### Final Total: ${final_subtotal:.2f}")
        
        with col_summary_2:
            if st.button("Clear Shopping Bag"):
                st.session_state.cart = {}
                st.rerun()

        st.markdown("---")
        st.subheader("Customer Details & Settlement")
        
        with st.form("checkout_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name *")
                email = st.text_input("Email Address *")
            with c2:
                phone = st.text_input("Phone Number *")
                address = st.text_input("Shipping Address *")
            
            payment_method = st.radio("Select Payment Settlement Channel", ["Cash App", "Zelle", "Venmo", "Cash POS (In-Person)"])
            notes = st.text_area("Special Instructions / Preorder Notes")
            
            submit = st.form_submit_button("Submit & Record Order")
            
            if submit:
                if name and email and phone and address:
                    items_str = ", ".join(summary_list)
                    
                    # Save directly to SQLite database
                    save_order_to_db(
                        name, email, phone, address, 
                        items_str, total_qty, raw_subtotal, 
                        discount, final_subtotal, payment_method, notes
                    )
                    
                    st.success(f"Order successfully placed for {name}!")
                    st.info(f"Please send payment of **${final_subtotal:.2f}** via **{payment_method}**.")
                    st.session_state.cart = {}
                else:
                    st.error("Please fill in all required fields marked with *.")

# TAB 3: ADMIN DASHBOARD (SQLITE BACKEND)
with tabs[2]:
    st.header("Admin Management Dashboard")
    
    admin_password = st.text_input("Enter Staff Password", type="password")
    
    if admin_password == "admin123":  # Default admin access key
        st.success("Authenticated as Staff")
        
        orders_df = get_all_orders()
        
        if orders_df.empty:
            st.info("No orders found in the database.")
        else:
            st.subheader("Recent Sales & Preorders")
            
            # Metrics Overview
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Orders", len(orders_df))
            m2.metric("Total Revenue", f"${orders_df['final_total'].sum():.2f}")
            m3.metric("Total Bottles Sold", int(orders_df['total_qty'].sum()))
            
            st.markdown("---")
            st.dataframe(orders_df, use_container_width=True)
            
            # Update Order Status
            st.subheader("Update Order Status")
            col_id, col_status, col_btn = st.columns([1, 2, 1])
            
            with col_id:
                selected_id = st.number_input("Order ID", min_value=1, step=1)
            with col_status:
                new_status = st.selectbox("Status", ["Pending Payment", "Paid / Processing", "Fulfilled / Shipped", "Cancelled"])
            with col_btn:
                st.write("")
                st.write("")
                if st.button("Update Status"):
                    update_order_status(selected_id, new_status)
                    st.success(f"Order #{selected_id} updated to {new_status}")
                    st.rerun()
    elif admin_password:
        st.error("Incorrect password.")

# ==========================================
# FOOTER & LEGAL DISCLAIMER
# ==========================================
st.markdown("---")
st.caption(f"**Legal Disclaimer:** {DISCLAIMER_TEXT}")
