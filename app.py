from datetime import datetime
import os
import random
import sqlite3
import string
import pandas as pd
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="T Fragrances | Storefront & POS",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="T Fragrances | Storefront & POS",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# DATABASE SETUP & AUTO-MIGRATION
# ==========================================
DB_FILE = "t_fragrances.db"
DEFAULT_STOCK_PER_ITEM = 5


def init_db():
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()

  try:
    c.execute("SELECT item_id FROM inventory LIMIT 1")
  except sqlite3.OperationalError:
    c.execute("DROP TABLE IF EXISTS inventory")
    c.execute("DROP TABLE IF EXISTS orders")

  c.execute("""
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
            is_priority INTEGER DEFAULT 0,
            cycle_id TEXT,
            notes TEXT,
            referral_code TEXT
        )
    """)

  c.execute("PRAGMA table_info(orders)")
  existing_cols = [col[1] for col in c.fetchall()]

  if "is_priority" not in existing_cols:
    c.execute("ALTER TABLE orders ADD COLUMN is_priority INTEGER DEFAULT 0")
  if "cycle_id" not in existing_cols:
    c.execute("ALTER TABLE orders ADD COLUMN cycle_id TEXT")
  if "notes" not in existing_cols:
    c.execute("ALTER TABLE orders ADD COLUMN notes TEXT")
  if "referral_code" not in existing_cols:
    c.execute("ALTER TABLE orders ADD COLUMN referral_code TEXT")

  c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            item_name TEXT,
            stock_level INTEGER,
            initial_stock INTEGER
        )
    """)

  c.execute("""
        CREATE TABLE IF NOT EXISTS gift_cards (
            code TEXT PRIMARY KEY,
            initial_value REAL,
            current_balance REAL,
            purchaser_name TEXT,
            recipient_email TEXT,
            status TEXT,
            created_date TEXT,
            payment_method TEXT
        )
    """)

  c.execute("PRAGMA table_info(gift_cards)")
  existing_gc_cols = [col[1] for col in c.fetchall()]
  if "payment_method" not in existing_gc_cols:
    c.execute("ALTER TABLE gift_cards ADD COLUMN payment_method TEXT")

  # Table for customer reviews and ratings
  c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_date TEXT,
            customer_name TEXT,
            rating INTEGER,
            item_id TEXT,
            review_text TEXT,
            is_approved INTEGER DEFAULT 1
        )
    """)

  conn.commit()
  conn.close()


init_db()

# ==========================================
# GLOBAL DISCLAIMERS & CATALOG DATA (SIGNATURE BLENDS ONLY)
# ==========================================
DISCLAIMER_TEXT = (
    "TF Fragrances offers proprietary, independently formulated scents"
    " inspired by popular fragrance profiles. Any reference to scent families or"
    " style impressions is strictly for descriptive purposes to give"
    " customers an idea of the olfactory notes. TF Fragrances does not use"
    " third-party trademarked names, nor are our products affiliated with,"
    " endorsed by, or sponsored by any third-party brands or manufacturers."
)

ALLERGY_DISCLAIMER_TEXT = (
    "⚠️ ALLERGY & SKIN SENSITIVITY NOTICE: T Fragrances products contain"
    " concentrated fragrance oils, essential oils, and aromatic compounds."
    " Please perform a patch test on a small area of skin before full"
    " application. Discontinue use immediately if redness, irritation, or"
    " itching occurs. Avoid contact with eyes, damaged skin, or open wounds."
    " Do not ingest. Keep out of reach of children and pets. T Fragrances"
    " assumes no liability for adverse allergic reaction or skin sensitivities."
)

FRAGRANCE_CATALOG = [
    {
        "id": "sig_m1",
        "name": "No 1 — Savage Spirit Blend",
        "gender": "Men",
        "category": "Signature Blend",
        "price": 45.0,
        "notes": (
            "Signature Blend No. 1 — Inspired by Sauvage profile: Crisp"
            " bergamot, pepper, and rich ambroxan."
        ),
        "profile_type": "fresh-citrus",
        "image_url": "savage_spirit.png",
    },
    {
        "id": "sig_m4",
        "name": "No 4 — Monarch Creed (Aventus Blend)",
        "gender": "Men",
        "category": "Signature Blend",
        "price": 45.0,
        "notes": (
            "Signature Blend No. 4 — Inspired by Aventus profile: Smoky"
            " pineapple, birchwood, and oakmoss."
        ),
        "profile_type": "smoky",
        "image_url": "aventus_blend.png",
    },
    {
        "id": "sig_w2",
        "name": "No 2 — Good Girl Blend",
        "gender": "Women",
        "category": "Signature Blend",
        "price": 45.0,
        "notes": (
            "Signature Blend No. 2 — Inspired by Good Girl profile: Tuberose,"
            " roasted tonka bean, and cocoa."
        ),
        "profile_type": "sweet-floral",
        "image_url": "good_girl_blend.png",
    },
    {
        "id": "sig_w3",
        "name": "No 3 — Crystal Rouge 540 Blend",
        "gender": "Women",
        "category": "Signature Blend",
        "price": 45.0,
        "notes": (
            "Signature Blend No. 3 — Inspired by Baccarat Rouge 540 profile:"
            " Jasmine, saffron, cedarwood, and ambergris."
        ),
        "profile_type": "woody",
        "image_url": "rouge_540_blend.png",
    },
]


def sync_inventory_defaults():
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()
  for item in FRAGRANCE_CATALOG:
    c.execute("SELECT stock_level FROM inventory WHERE item_id = ?", (item["id"],))
    row = c.fetchone()
    if not row:
      c.execute(
          "INSERT INTO inventory (item_id, item_name, stock_level,"
          " initial_stock) VALUES (?, ?, ?, ?)",
          (
              item["id"],
              item["name"],
              DEFAULT_STOCK_PER_ITEM,
              DEFAULT_STOCK_PER_ITEM,
          ),
      )
  conn.commit()
  conn.close()


sync_inventory_defaults()


# Database Helper Functions
def get_current_30_day_cycle():
  now = datetime.now()
  start_of_year = datetime(now.year, 1, 1)
  days_passed = (now - start_of_year).days
  cycle_num = (days_passed // 30) + 1
  return f"CYCLE-{now.year}-30D-{cycle_num:02d}"


def save_order_to_db(
    name,
    email,
    phone,
    address,
    items_summary,
    qty,
    subtotal,
    discount,
    total,
    payment_method,
    is_priority,
    notes,
    cart_items,
    referral_code="",
):
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()
  order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  cycle_id = get_current_30_day_cycle()
  status = "Payment Sent / Pending Verification" if is_priority else "Pending"

  c.execute(
      """
        INSERT INTO orders (
            order_date, customer_name, customer_email, customer_phone, 
            shipping_address, items_summary, total_qty, subtotal, 
            discount_applied, final_total, payment_method, status, is_priority, cycle_id, notes, referral_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          order_date,
          name,
          email,
          phone,
          address,
          items_summary,
          qty,
          subtotal,
          discount,
          total,
          payment_method,
          status,
          int(is_priority),
          cycle_id,
          notes,
          referral_code,
      ),
  )

  for item_id, item_qty in cart_items.items():
    c.execute(
        "UPDATE inventory SET stock_level = stock_level - ? WHERE item_id = ?",
        (item_qty, item_id),
    )

  conn.commit()
  conn.close()


def search_orders(query, is_admin=False):
  conn = sqlite3.connect(DB_FILE)
  q = f"%{query}%"
  if is_admin:
    df = pd.read_sql_query(
        "SELECT * FROM orders WHERE id LIKE ? OR customer_name LIKE ? OR"
        " customer_email LIKE ? OR customer_phone LIKE ? ORDER BY id DESC",
        conn,
        params=(q, q, q, q),
    )
  else:
    df = pd.read_sql_query(
        "SELECT id, order_date, customer_name, items_summary, total_qty,"
        " final_total, status, is_priority, cycle_id, referral_code FROM orders"
        " WHERE customer_email LIKE ? OR customer_phone LIKE ? ORDER BY id DESC",
        conn,
        params=(q, q),
    )
  conn.close()
  return df


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


def get_inventory_status():
  conn = sqlite3.connect(DB_FILE)
  df = pd.read_sql_query("SELECT * FROM inventory", conn)
  conn.close()
  return df


def update_item_stock(item_id, new_stock):
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()
  c.execute(
      "UPDATE inventory SET stock_level = ? WHERE item_id = ?",
      (new_stock, item_id),
  )
  conn.commit()
  conn.close()


def get_gift_card(code):
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()
  c.execute("SELECT * FROM gift_cards WHERE code = ?", (code,))
  row = c.fetchone()
  conn.close()
  return row


def save_review(customer_name, rating, item_id, review_text):
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()
  review_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  c.execute(
      """
        INSERT INTO reviews (review_date, customer_name, rating, item_id, review_text, is_approved)
        VALUES (?, ?, ?, ?, ?, 1)
    """,
      (review_date, customer_name, rating, item_id, review_text),
  )
  conn.commit()
  conn.close()


def get_approved_reviews(item_id=None):
  conn = sqlite3.connect(DB_FILE)
  if item_id and item_id != "All":
    df = pd.read_sql_query(
        "SELECT * FROM reviews WHERE is_approved = 1 AND item_id = ? ORDER BY id DESC",
        conn,
        params=(item_id,),
    )
  else:
    df = pd.read_sql_query(
        "SELECT * FROM reviews WHERE is_approved = 1 ORDER BY id DESC", conn
    )
  conn.close()
  return df


# ==========================================
# SESSION STATE & CART
# ==========================================
if "cart" not in st.session_state:
  st.session_state.cart = {}
if "applied_gift_card" not in st.session_state:
  st.session_state.applied_gift_card = None
if "gift_card_discount" not in st.session_state:
  st.session_state.gift_card_discount = 0.0


def add_to_cart(item_id):
  if item_id in st.session_state.cart:
    st.session_state.cart[item_id] += 1
  else:
    st.session_state.cart[item_id] = 1
  st.toast("Added to bag!", icon="🛍️")


# ==========================================
# URL QUERY PARAMS FOR REFERRAL TRACKING
# ==========================================
PARTNER_MAPPING = {
    "alex": "Alexander Thompson",
    "jameka": "Jameka Hatton",
    "ray": "Ira Ray Thompson",
    "eq": "Eriq Dior",
}

query_params = st.query_params
active_referral = query_params.get("ref", "").strip().lower()

if active_referral in PARTNER_MAPPING:
  st.session_state["active_ref"] = PARTNER_MAPPING[active_referral]
elif active_referral:
  st.session_state["active_ref"] = active_referral
else:
  if "active_ref" not in st.session_state:
    st.session_state["active_ref"] = ""

current_ref_tag = st.session_state.get("active_ref", "")

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("✨ T Fragrances")
st.sidebar.caption("50ml Clear Bottle Luxury Impressions")

if current_ref_tag:
  st.sidebar.success(f"🔗 Partner Tracking Ref: **{current_ref_tag}**")

search_term = st.sidebar.text_input("🔍 Search signature catalog...", "").lower()
selected_gender = st.sidebar.radio("Collection Filter", ["All", "Men", "Women"])
priority_only = st.sidebar.checkbox("🔥 Show Priority Preorders Only")

# ==========================================
# SIDEBAR - QR CODE & TABBED PAYMENT OPTIONS
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("📲 Scan to Order & Pay")

if os.path.exists("qr_code.png"):
  st.sidebar.image(
      "qr_code.png",
      caption="Scan for QR Portal (More Scents & Home Scents)",
      use_container_width=True,
  )
else:
  st.sidebar.info("Place your QR image file as 'qr_code.png' in root directory.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💳 Quick Payment Options")

pay_tab1, pay_tab2, pay_tab3 = st.sidebar.tabs(["Cash App", "Venmo", "Zelle"])

with pay_tab1:
  st.markdown("**Jameka Howell**")
  st.markdown("`$JaMekaHowell`")
  if os.path.exists("cashapp_qr.png"):
    st.image("cashapp_qr.png", use_container_width=True)
  else:
    st.info("Upload cashapp_qr.png")

with pay_tab2:
  st.markdown("**Jameka Hatton**")
  st.markdown("`@Jameka-Hatton`")
  if os.path.exists("venmo_qr.png"):
    st.image("venmo_qr.png", use_container_width=True)
  else:
    st.info("Upload venmo_qr.png")

with pay_tab3:
  st.markdown("**Alexander Thompson**")
  st.markdown("`8632364196`")
  if os.path.exists("zelle_qr.png"):
    st.image("zelle_qr.png", use_container_width=True)
  else:
    st.info("Upload zelle_qr.png")

# ==========================================
# SIDEBAR - SHOPPING BAG SUMMARY
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Shopping Bag Summary")

total_qty = sum(st.session_state.cart.values())
raw_subtotal = sum(
    next(item["price"] for item in FRAGRANCE_CATALOG if item["id"] == i_id) * qty
    for i_id, qty in st.session_state.cart.items()
)

discount = 0.0
discount_label = ""

if raw_subtotal >= 100.0:
  discount = 0.20
  discount_label = "20% OFF (Spend $100+ Tier)"
elif total_qty >= 3:
  discount = 0.15
  discount_label = "15% OFF (3+ Items Tier)"
elif total_qty == 2:
  discount = 0.10
  discount_label = "10% OFF (2 Items Tier)"

subtotal_after_volume = raw_subtotal * (1 - discount)
final_subtotal = max(
    0.0, subtotal_after_volume - st.session_state.gift_card_discount
)

st.sidebar.write(f"**Items in Bag:** {total_qty}")
if discount > 0:
  st.sidebar.write(f"**Volume Discount:** {discount_label}")
if st.session_state.applied_gift_card:
  st.sidebar.write(
      f"**Gift Card Applied:** -${st.session_state.gift_card_discount:.2f}"
  )
st.sidebar.subheader(f"Total: ${final_subtotal:.2f}")

# ==========================================
# MAIN INTERFACE
# ==========================================
st.title("T Fragrances")

# --- NATIVE GITHUB RAW MP4 VIDEO PLAYER ---
st.video(
    "https://raw.githubusercontent.com/KingAlex2220/T-Fragrances-/main/deevid_video_33065096.mp4"
)

st.info(
    "💡 **Looking for something else?**,"
    " scan the **QR code** in the sidebar to access our full catalog portal,"
    " where you can request any other scent impressions and explore our"
    " exclusive **Home Scents** collection!"
)

st.info(
    "📦 **Shipping Notice:** All orders are processed and shipped out within"
    " **3–5 business days** after payment verification. Thank you for your"
    " patience and support!"
)

with st.expander("ℹ️ Legal, Brand & Allergy Notices"):
  st.write(f"**Trademark Notice:** {DISCLAIMER_TEXT}")
  st.write("---")
  st.warning(ALLERGY_DISCLAIMER_TEXT)

filtered_catalog = FRAGRANCE_CATALOG

if selected_gender != "All":
  filtered_catalog = [
      x for x in filtered_catalog if x["gender"] == selected_gender
  ]

if search_term:
  filtered_catalog = [
      x
      for x in filtered_catalog
      if search_term in x["name"].lower()
      or search_term in x["notes"].lower()
      or search_term in x["category"].lower()
  ]

inventory_df = get_inventory_status().set_index("item_id")

if priority_only:
  filtered_catalog = [
      x
      for x in filtered_catalog
      if (
          inventory_df.loc[x["id"], "stock_level"]
          if x["id"] in inventory_df.index
          else 5
      )
      <= 0
  ]

tabs = st.tabs([
    "✨ Signature Blends",
    "📲 QR Code Request Portal",
    "🎁 Gift Cards",
    "⭐ Reviews & Testimonials",
    "🛒 Checkout & Invoice",
    "🔍 Customer Order Lookup",
    "🔒 Master Admin & Inventory",
])

# ------------------------------------------
# TAB 1: SIGNATURE BLENDS
# ------------------------------------------
with tabs[0]:
  st.header("T Fragrances Signature Blends")
  st.caption(
      "Featuring our exclusive signature 4 blends ($45.00 each). Men's blends"
      " (No. 1 & No. 4) and Women's blends (No. 2 & No. 3)."
  )

  cols = st.columns(2)
  for idx, item in enumerate(filtered_catalog):
    col = cols[idx % 2]
    stock_level = (
        inventory_df.loc[item["id"], "stock_level"]
        if item["id"] in inventory_df.index
        else 5
    )

    with col:
      with st.container(border=True):
        image_path = item.get("image_url")
        if image_path and (
            image_path.startswith("http") or os.path.exists(image_path)
        ):
          img_col, text_col = st.columns([1, 1.3])
          with img_col:
            with st.popover("🔍 Tap to Enlarge Photo"):
              st.image(image_path, use_container_width=True)
            st.image(image_path, use_container_width=True)
          with text_col:
            st.markdown(f"### {item['name']}")
            st.caption(f"**{item['gender']}'s** • {item['category']}")
            st.write(f"*{item['notes']}*")
            st.subheader(f"${item['price']:.2f}")
        else:
          st.markdown(f"### {item['name']}")
          st.caption(f"**{item['gender']}'s** • {item['category']}")
          st.write(f"*{item['notes']}*")
          st.subheader(f"${item['price']:.2f}")

        if stock_level <= 0:
          st.error("🔥 Out of Stock — Priority Preorder Available")
        elif stock_level <= 2:
          st.warning(f"⚠️ Low Stock: Only {stock_level} left!")
        else:
          st.caption(f"Stock: {stock_level} available")

        st.button(
            "Add to Bag",
            key=f"btn_{item['id']}",
            on_click=add_to_cart,
            args=(item["id"],),
        )

# ------------------------------------------
# TAB 2: QR CODE REQUEST PORTAL
# ------------------------------------------
with tabs[1]:
  st.header("📲 QR Code Impression & Home Scents Request Portal")
  st.info(
      "✨ **Notice:** You are ordering 100% oil-based designer style"
      " impressions or **Home Scents** of the products you see scanned from the"
      " QR code ($45.00 per bottle/unit)."
  )

  with st.form("qr_request_line_form"):
    qr_cust_name = st.text_input("Your Full Name *")
    qr_cust_contact = st.text_input("Email or Phone Number *")
    qr_shipping_address = st.text_input("Delivery / Shipping Address *")

    st.markdown("---")
    st.markdown("### Request Line (Scents & Home Scents)")
    st.write(
        "Simply type out the name of the impression or home scent you want to"
        " request from the QR code sheet, along with the quantity desired."
    )

    qr_item_requests = st.text_area(
        "What impressions or home scents would you like to request? (e.g., 1x"
        " Home Scent Reed Diffuser blend, or other brand impressions) *"
    )
    qr_total_qty = st.number_input(
        "Total Number of Items Requested", min_value=1, value=1
    )

    qr_payment_method = st.selectbox(
        "Preferred Settlement Method",
        ["Cash App", "Zelle", "Venmo", "Cash POS (In-Person)"],
    )
    qr_notes = st.text_area(
        "Additional Request Notes / Custom Preferences / Home Scent Details"
    )

    qr_submit = st.form_submit_button("Submit QR Request")

    if qr_submit:
      if not (qr_cust_name and qr_cust_contact and qr_shipping_address):
        st.error(
            "Please fill in your name, contact details, and shipping address."
        )
      elif not qr_item_requests:
        st.error(
            "Please specify the impressions or home scents you want to request"
            " from the QR code."
        )
      else:
        qr_subtotal = qr_total_qty * 45.0

        qr_discount = 0.0
        if qr_subtotal >= 100.0:
          qr_discount = 0.20
        elif qr_total_qty >= 3:
          qr_discount = 0.15
        elif qr_total_qty == 2:
          qr_discount = 0.10

        qr_final_total = qr_subtotal * (1 - qr_discount)

        save_order_to_db(
            name=qr_cust_name,
            email=qr_cust_contact,
            phone=qr_cust_contact,
            address=qr_shipping_address,
            items_summary=qr_item_requests,
            qty=qr_total_qty,
            subtotal=qr_subtotal,
            discount=qr_discount,
            total=qr_final_total,
            payment_method=qr_payment_method,
            is_priority=1,
            notes=(
                "QR Code Custom Request Order (Scents / Home Scents)."
                f" Desired Items: {qr_item_requests}. "
                + (qr_notes if qr_notes else "")
            ),
            cart_items={},
            referral_code=current_ref_tag,
        )

        st.success(
            f"Success! Your request for {qr_total_qty} item(s) has been"
            f" submitted for {qr_cust_name}."
        )
        st.info(
            f"Please complete your settlement of **${qr_final_total:.2f}** via"
            f" **{qr_payment_method}** using the payment handles in the"
            " sidebar."
        )

# ------------------------------------------
# TAB 3: GIFT CARDS
# ------------------------------------------
with tabs[2]:
  st.header("🎁 Digital Gift Cards & Store Credit")
  st.markdown(
      "Purchase a digital gift card for friends or family, or redeem an active"
      " gift card code toward your order."
  )

  gc_tab1, gc_tab2 = st.tabs(["Purchase Gift Card", "Redeem Gift Card Code"])

  with gc_tab1:
    with st.form("purchase_gc_form"):
      gc_purchaser = st.text_input("Your Name *")
      gc_recipient = st.text_input("Recipient Email or Name *")
      gc_value = st.number_input(
          "Gift Card Amount ($)", min_value=10.0, value=45.0, step=5.0
      )
      gc_payment_method = st.selectbox(
          "Settlement Method Used *",
          ["Cash App", "Zelle", "Venmo", "Cash POS (In-Person)"],
      )

      gc_payment_confirmed = st.checkbox(
          "✅ I confirm that payment has been sent/collected via the selected"
          " method."
      )

      gc_submit = st.form_submit_button("Generate Gift Card Code")

      if gc_submit:
        if not (gc_purchaser and gc_recipient):
          st.error("Please fill in both your name and recipient's details.")
        elif not gc_payment_confirmed:
          st.error(
              "⚠️ You must confirm that payment has been sent before generating"
              " a code."
          )
        else:
          random_str = "".join(
              random.choices(string.ascii_uppercase + string.digits, k=6)
          )
          gc_code = f"TF-GC-{random_str}"

          conn = sqlite3.connect(DB_FILE)
          c = conn.cursor()
          created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          c.execute(
              """
                INSERT OR REPLACE INTO gift_cards (code, initial_value, current_balance, purchaser_name, recipient_email, status, created_date, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
              (
                  gc_code,
                  gc_value,
                  gc_value,
                  gc_purchaser,
                  gc_recipient,
                  "Pending Verification",
                  created_date,
                  gc_payment_method,
              ),
          )
          conn.commit()
          conn.close()

          st.success("🎉 Gift Card Created (Pending Verification)!")
          st.info(
              f"**Gift Card Code:** `{gc_code}` | **Value:** ${gc_value:.2f} |"
              f" **Via:** {gc_payment_method}"
          )

  with gc_tab2:
    with st.form("redeem_gc_form"):
      entered_code = st.text_input(
          "Enter Gift Card Code (e.g., TF-GC-XXXXXX)"
      ).strip()
      redeem_submit = st.form_submit_button("Apply Gift Card to Order")

      if redeem_submit:
        card_data = get_gift_card(entered_code.upper())
        if not card_data:
          st.error("Invalid gift card code.")
        else:
          balance = card_data[2]
          status = card_data[5]
          if status != "Active" or balance <= 0:
            st.warning(
                "⚠️ This gift card is either pending admin verification, has a"
                " zero balance, or is inactive."
            )
          else:
            st.session_state.applied_gift_card = entered_code.upper()
            st.session_state.gift_card_discount = balance
            st.success(
                f"✅ Gift card applied! Available Balance: ${balance:.2f}"
            )
            st.rerun()

# ------------------------------------------
# TAB 4: REVIEWS & TESTIMONIALS
# ------------------------------------------
with tabs[3]:
  st.header("⭐ Customer Reviews & Testimonials")
  st.markdown(
      "Read what our community has to say about our luxury fragrance"
      " impressions, or leave your own review below!"
  )

  rev_sub_tab1, rev_sub_tab2 = st.tabs(["Browse Reviews", "Leave a Review"])

  with rev_sub_tab1:
    catalog_options = ["All"] + [item["name"] for item in FRAGRANCE_CATALOG]
    filter_item_name = st.selectbox(
        "Filter Reviews by Product Blend", catalog_options
    )

    selected_item_id_for_review = "All"
    if filter_item_name != "All":
      selected_item_id_for_review = next(
          item["id"] for item in FRAGRANCE_CATALOG if item["name"] == filter_item_name
      )

    reviews_df = get_approved_reviews(selected_item_id_for_review)

    if reviews_df.empty:
      st.info(
          "No reviews found for this selection yet. Be the first to leave one!"
      )
    else:
      avg_rating = reviews_df["rating"].mean()
      st.metric(
          "Average Community Rating",
          f"{avg_rating:.1f} / 5.0 ⭐",
          f"{len(reviews_df)} total review(s)",
      )
      st.markdown("---")

      for _, row in reviews_df.iterrows():
        stars = "⭐" * int(row["rating"])
        match_blend = next(
            (item["name"] for item in FRAGRANCE_CATALOG if item["id"] == row["item_id"]),
            "General Store Review",
        )
        with st.container(border=True):
          st.markdown(f"**{row['customer_name']}** — {stars}")
          st.caption(f"Product: {match_blend} | Date: {row['review_date']}")
          st.write(f'"{row["review_text"]}"')

  with rev_sub_tab2:
    with st.form("leave_review_form"):
      st.markdown("### Share Your Experience")
      rev_name = st.text_input("Your Name *")
      rev_rating = st.slider("Rating (1 to 5 Stars)", min_value=1, max_value=5, value=5)
      
      blend_choices = {item["name"]: item["id"] for item in FRAGRANCE_CATALOG}
      blend_choices["General Store / QR Request Experience"] = "general"
      
      chosen_blend_name = st.selectbox("Select Fragrance / Product", list(blend_choices.keys()))
      rev_text = st.text_area("Your Review / Testimonial *")
      
      submit_review = st.form_submit_button("Submit Review")

      if submit_review:
        if not (rev_name and rev_text):
          st.error("Please provide your name and your review message.")
        else:
          target_blend_id = blend_choices[chosen_blend_name]
          save_review(rev_name, rev_rating, target_blend_id, rev_text)
          st.success("🎉 Thank you! Your review has been successfully submitted.")

# ------------------------------------------
# TAB 5: CHECKOUT & INVOICE GENERATOR
# ------------------------------------------
with tabs[4]:
  st.header("🧾 Checkout & Invoice Generator")

  if not st.session_state.cart:
    st.info("Your bag is currently empty.")
  else:
    st.subheader("Selected Signature Blends")
    cart_data = []
    summary_list = []

    for item_id, qty in st.session_state.cart.items():
      product = next(p for p in FRAGRANCE_CATALOG if p["id"] == item_id)
      cart_data.append({
          "Product Name": product["name"],
          "Category": product["category"],
          "Qty": qty,
          "Price": f"${product['price']:.2f}",
          "Total": f"${product['price'] * qty:.2f}",
      })
      summary_list.append(f"{qty}x {product['name']}")

    st.table(pd.DataFrame(cart_data))

    c1, c2 = st.columns(2)
    with c1:
      st.markdown(f"**Total Items:** {total_qty}")
      st.markdown(
          f"**Applied Discount Tier:**"
          f" {discount_label if discount > 0 else 'None'}"
      )
      if st.session_state.applied_gift_card:
        st.markdown(
            f"**Gift Card Active:** {st.session_state.applied_gift_card}"
            f" (-${st.session_state.gift_card_discount:.2f})"
        )
    with c2:
      if st.button("Clear Bag"):
        st.session_state.cart = {}
        st.session_state.applied_gift_card = None
        st.session_state.gift_card_discount = 0.0
        st.rerun()

    st.markdown("---")

    # --- LIVE INVOICE DISPLAY BOX ---
    st.markdown("### 📄 Generated Customer Invoice")
    invoice_container = st.container(border=True)
    with invoice_container:
      inv_col1, inv_col2 = st.columns(2)
      with inv_col1:
        st.markdown("**T Fragrances**")
        st.markdown("100% Oil-Based Luxury Impressions")
        st.markdown(f"**Invoice Date:** {datetime.now().strftime('%Y-%m-%d')}")
        st.markdown(f"**Master Cycle:** {get_current_30_day_cycle()}")
        if current_ref_tag:
          st.markdown(f"**Partner Referral:** {current_ref_tag}")
      with inv_col2:
        st.markdown(f"**Subtotal (Raw):** ${raw_subtotal:.2f}")
        if discount > 0:
          st.markdown(
              f"**Discount ({discount_label}):** -${raw_subtotal * discount:.2f}"
          )
        if st.session_state.applied_gift_card:
          st.markdown(
              f"**Gift Card Credit:**"
              f" -${st.session_state.gift_card_discount:.2f}"
          )
        st.markdown(f"### **Total Due: ${final_subtotal:.2f}**")

      st.markdown("---")
      st.markdown("### 💳 Designated Payment Destination Info")
      st.write(
          "Please send your exact invoice total to one of the following"
          " authorized channels before confirming your order:"
      )

      pay_info_col1, pay_info_col2, pay_info_col3 = st.columns(3)
      with pay_info_col1:
        st.markdown("**Cash App**")
        st.markdown("Name: **Jameka Howell**")
        st.markdown("Handle: `$JaMekaHowell`")
      with pay_info_col2:
        st.markdown("**Venmo**")
        st.markdown("Name: **Jameka Hatton**")
        st.markdown("Handle: `@Jameka-Hatton`")
      with pay_info_col3:
        st.markdown("**Zelle**")
        st.markdown("Name: **Alexander Thompson**")
        st.markdown("Phone/ID: `8632364196`")

    st.markdown("---")
    st.subheader("Customer Shipping & Payment Submission Form")

    with st.form("checkout_form"):
      col_a, col_b = st.columns(2)
      with col_a:
        name = st.text_input("Full Name *")
        email = st.text_input("Email Address *")
      with col_b:
        phone = st.text_input("Phone Number *")
        address = st.text_input("Shipping Address *")

      # Manual referral override option if they weren't tracked via URL link
      manual_ref = st.text_input(
          "Partner / Affiliate Referral Tag (Optional if referred by a partner)",
          value=current_ref_tag,
      )

      payment_method = st.radio(
          "Select Settlement Channel Used",
          ["Cash App", "Zelle", "Venmo", "Cash POS (In-Person)"],
      )
      is_priority = st.checkbox(
          "🔥 Mark as Priority Preorder (Bypasses standard queue for fastest"
          " fulfillment)"
      )
      notes = st.text_area("Special Delivery Instructions / Scent Preferences")

      st.markdown("---")
      st.caption("⚠️ **Safety & Payment Confirmation Checkboxes**")

      payment_confirmed = st.checkbox(
          "✅ I confirm that I have sent the exact payment total of "
          f"${final_subtotal:.2f} to the designated payment handle above."
      )

      allergy_ack = st.checkbox(
          "I acknowledge that I have read the Allergy & Skin Sensitivity"
          " Disclaimer and agree to perform a skin patch test prior to use."
      )

      if st.form_submit_button("Submit Order"):
        if not (name and email and phone and address):
          st.error("Please fill in all required customer fields.")
        elif not payment_confirmed:
          st.error(
              "⚠️ You must check the confirmation box verifying that you have"
              " sent the payment before submitting your order."
          )
        elif not allergy_ack:
          st.error(
              "Please acknowledge the Safety & Allergy Disclaimer prior to"
              " completing your order."
          )
        else:
          items_str = ", ".join(summary_list)
          final_tag_to_save = manual_ref.strip().lower() if manual_ref else current_ref_tag

          save_order_to_db(
              name,
              email,
              phone,
              address,
              items_str,
              total_qty,
              raw_subtotal,
              discount,
              final_subtotal,
              payment_method,
              is_priority,
              notes,
              st.session_state.cart,
              referral_code=final_tag_to_save,
          )

          if st.session_state.applied_gift_card:
            conn_gc = sqlite3.connect(DB_FILE)
            c_gc = conn_gc.cursor()
            c_gc.execute(
                "UPDATE gift_cards SET current_balance = 0, status = 'Redeemed'"
                " WHERE code = ?",
                (st.session_state.applied_gift_card,),
            )
            conn_gc.commit()
            conn_gc.close()

          st.success(
              f"Order and payment verification successfully submitted for"
              f" {name}!"
          )
          if is_priority:
            st.warning(
                "⚡ Priority Preorder activated. Production scheduled on"
                " fast-track timeline."
            )
          st.session_state.cart = {}
          st.session_state.applied_gift_card = None
          st.session_state.gift_card_discount = 0.0

# ------------------------------------------
# TAB 6: CUSTOMER ORDER LOOKUP
# ------------------------------------------
with tabs[5]:
  st.header("🔍 Customer Order Lookup Portal")
  st.write("Track active order status, preorders, and fulfillment updates.")

  user_query = st.text_input(
      "Enter your registered Email Address or Phone Number:"
  )
  if st.button("Lookup Order Status") and user_query:
    results = search_orders(user_query, is_admin=False)
    if results.empty:
      st.warning("No matching orders found. Please verify your details.")
    else:
      st.subheader(f"Found {len(results)} Order(s)")
      for idx, row in results.iterrows():
        with st.expander(
            f"Order #{row['id']} — Status: {row['status']}"
            f" ({row['order_date']})"
        ):
          st.write(f"**30-Day Master Cycle ID:** {row['cycle_id']}")
          st.write(f"**Purchased Items:** {row['items_summary']}")
          st.write(f"**Total Bottles:** {row['total_qty']}")
          st.write(f"**Total Amount:** ${row['final_total']:.2f}")
          if row["referral_code"]:
            st.write(f"**Partner Referral Tag:** {row['referral_code']}")
          if row["is_priority"]:
            st.warning("🔥 Priority Preorder Queue Active")

# ------------------------------------------
# TAB 7: MASTER ADMIN & RESTOCKING TOOL
# ------------------------------------------
with tabs[6]:
  st.header("🔒 Master Admin Database & Restocking Management")
  admin_pwd = st.text_input("Enter Admin Security Password", type="password")

  if admin_pwd == "Safe9uard-tf80":
    st.success("Staff Authentication Verified")

    # --- PARTNERSHIP & AFFILIATE PERFORMANCE TRACKER ---
    st.subheader("🤝 Partner & Affiliate Performance Tracker")
    st.caption("Review sales volume, orders, and attribution tracked via unique referral links (e.g. `?ref=name`).")
    
    conn_aff = sqlite3.connect(DB_FILE)
    aff_df = pd.read_sql_query("SELECT referral_code, final_total, total_qty FROM orders WHERE referral_code IS NOT NULL AND referral_code != ''", conn_aff)
    conn_aff.close()

    if aff_df.empty:
      st.info("No partner-attributed orders recorded yet. Share links using `?ref=partnername`.")
    else:
      partner_summary = aff_df.groupby("referral_code").agg(
          Total_Orders=("final_total", "count"),
          Total_Bottles=("total_qty", "sum"),
          Total_Revenue=("final_total", "sum")
      ).reset_index()
      partner_summary.columns = ["Partner Tag", "Orders Generated", "Bottles Sold", "Gross Revenue ($)"]
      st.dataframe(partner_summary, use_container_width=True)

    st.markdown("---")

    st.subheader("🎁 Gift Card Management & Verification")
    conn_gc_admin = sqlite3.connect(DB_FILE)
    gc_df = pd.read_sql_query("SELECT * FROM gift_cards ORDER BY created_date DESC", conn_gc_admin)
    conn_gc_admin.close()

    if gc_df.empty:
      st.info("No gift cards generated yet.")
    else:
      st.dataframe(gc_df, use_container_width=True)

      gc_col1, gc_col2, gc_col3 = st.columns([2, 2, 1])
      with gc_col1:
        target_gc_code = st.selectbox("Select Gift Card Code to Update", gc_df["code"].tolist())
      with gc_col2:
        new_gc_status = st.selectbox("Set Gift Card Status", ["Active", "Pending Verification", "Redeemed", "Disabled"])
      with gc_col3:
        st.write("")
        st.write("")
        if st.button("Update GC Status"):
          conn_up = sqlite3.connect(DB_FILE)
          c_up = conn_up.cursor()
          c_up.execute("UPDATE gift_cards SET status = ? WHERE code = ?", (new_gc_status, target_gc_code))
          conn_up.commit()
          conn_up.close()
          st.success(f"Gift card {target_gc_code} status updated to {new_gc_status}!")
          st.rerun()

    st.markdown("---")

    st.subheader("📦 Inventory Tracking & Restocking Tool")
    st.caption(
        "Default Stock Level: 5 bottles. Low stock alerts trigger at 2 or fewer"
        " bottles."
    )

    inv_df = get_inventory_status()
    inv_df["Status"] = inv_df["stock_level"].apply(
        lambda x: (
            "🚨 CRITICAL LOW (≤2)"
            if x <= 2
            else ("⚠️ LOW (3)" if x == 3 else "✅ OK")
        )
    )

    low_stock_items = inv_df[inv_df["stock_level"] <= 2]
    if not low_stock_items.empty:
      st.error(
          f"⚠️ **RESTOCK ALERT:** {len(low_stock_items)} items are running low"
          " or out of stock!"
      )
      st.dataframe(
          low_stock_items[["item_id", "item_name", "stock_level", "Status"]],
          use_container_width=True,
      )
    else:
      st.success("All signature stock levels are fully operational.")

    with st.expander("🛠️ Restock Tool — Batch or Single Item Update"):
      stock_col1, stock_col2, stock_col3 = st.columns([2, 1, 1])
      with stock_col1:
        selected_item_id = st.selectbox(
            "Select Blend to Restock",
            inv_df["item_id"] + " - " + inv_df["item_name"],
        )
        target_id = selected_item_id.split(" - ")[0]
      with stock_col2:
        new_qty = st.number_input("Set Restock Quantity", min_value=0, value=5)
      with stock_col3:
        st.write("")
        st.write("")
        if st.button("Apply Restock"):
          update_item_stock(target_id, new_qty)
          st.success("Inventory stock successfully updated!")
          st.rerun()

    st.markdown("---")

    st.subheader("🗓️ Master Order Database & Partner Attribution")

    orders_df = get_all_orders()

    if orders_df.empty:
      st.info("No orders currently recorded in the master database.")
    else:
      cycles = orders_df["cycle_id"].unique().tolist()
      selected_cycle = st.selectbox(
          "Filter Master Database by 30-Day Cycle Window",
          ["All Cycles"] + cycles,
      )

      display_orders = (
          orders_df
          if selected_cycle == "All Cycles"
          else orders_df[orders_df["cycle_id"] == selected_cycle]
      )

      m1, m2, m3, m4 = st.columns(4)
      m1.metric("Total Cycle Orders", len(display_orders))
      m2.metric("Gross Revenue", f"${display_orders['final_total'].sum():.2f}")
      m3.metric("Total Bottles Sold", int(display_orders["total_qty"].sum()))
      m4.metric("Priority Preorders", int(display_orders["is_priority"].sum()))

      st.dataframe(display_orders, use_container_width=True)

      st.subheader("Update Processing Status & Priority Preorders")
      u1, u2, u3 = st.columns([1, 2, 1])
      with u1:
        target_order_id = st.number_input(
            "Target Order ID", min_value=1, step=1
        )
      with u2:
        status_option = st.selectbox(
            "Set New Processing Status",
            [
                "Pending Payment",
                "Payment Sent / Pending Verification",
                "Paid / In Production",
                "Fulfilled / Shipped",
                "Cancelled",
            ],
        )
      with u3:
        st.write("")
        st.write("")
        if st.button("Update Order Status"):
          update_order_status(target_order_id, status_option)
          st.success(f"Order #{target_order_id} updated!")
          st.rerun()

  elif admin_pwd:
    st.error("Invalid Security Password.")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption(f"**Legal Disclaimer:** {DISCLAIMER_TEXT}")
st.caption(f"{ALLERGY_DISCLAIMER_TEXT}")

# ==========================================
# CUSTOM SIDEBAR ELLIPSIS MENU & THEME SWITCHER
# ==========================================
with st.sidebar:
    st.markdown("<br><br><br>" * 3, unsafe_allow_html=True) 
    st.divider() 
    
    with st.expander("⋮ System Settings & Options", expanded=False):
        st.write("🎨 **Appearance & Theme**")
        
        theme_choice = st.selectbox(
            "Select Theme Mode",
            options=["Light Mode", "Dark Mode", "Midnight Blue"],
            key="app_theme_selection"
        )
        
        if theme_choice == "Dark Mode":
            st.markdown("""
                <style>
                .stApp { background-color: #0E1117 !important; color: #FAFAFA !important; }
                section[data-testid="stSidebar"] { background-color: #1A1C23 !important; }
                div[data-testid="stExpander"] { background-color: #262730 !important; color: #FAFAFA !important; }
                div[data-testid="stExpander"] * { color: #FAFAFA !important; }
                select, label { color: #FAFAFA !important; }
                button[data-baseweb="tab"] { color: #8A99AD !important; }
                button[data-baseweb="tab"][aria-selected="true"] { color: #FAFAFA !important; border-color: #FAFAFA !important; }
                div[data-testid="stTextInput"] > div { background-color: #262730 !important; color: #FAFAFA !important; }
                div[data-testid="stTextInput"] input { color: #FAFAFA !important; }
                .stApp button { background-color: #262730 !important; border: 1px solid #4A4A4A !important; }
                .stApp button p { color: #FAFAFA !important; }
                </style>
            """, unsafe_allow_html=True)
            
        elif theme_choice == "Midnight Blue":
            st.markdown("""
                <style>
                .stApp { background-color: #0A192F !important; color: #8892B0 !important; }
                section[data-testid="stSidebar"] { background-color: #172A45 !important; }
                div[data-testid="stExpander"] { background-color: #112240 !important; color: #8892B0 !important; }
                div[data-testid="stExpander"] * { color: #64FFDA !important; }
                select, label { color: #64FFDA !important; }
                button[data-baseweb="tab"] { color: #8892B0 !important; }
                button[data-baseweb="tab"][aria-selected="true"] { color: #64FFDA !important; border-color: #64FFDA !important; }
                div[data-testid="stTextInput"] > div { background-color: #112240 !important; color: #64FFDA !important; }
                div[data-testid="stTextInput"] input { color: #64FFDA !important; }
                .stApp button { background-color: #112240 !important; border: 1px solid #64FFDA !important; }
                .stApp button p { color: #64FFDA !important; }
                </style>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
                <style>
                .stApp { background-color: #FFFFFF !important; color: #31333F !important; }
                section[data-testid="stSidebar"] { background-color: #F0F2F6 !important; }
                
                .stApp p, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp li { 
                    color: #31333F !important; 
                }
                
                div[data-testid="stExpander"] { background-color: #FFFFFF !important; border: 1px solid #D3D3D3 !important; }
                div[data-testid="stExpander"] summary { background-color: #F0F2F6 !important; color: #31333F !important; }
                div[data-testid="stExpander"] summary * { color: #31333F !important; }
                div[data-testid="stExpander"] * { color: #31333F !important; }
                
                div[data-baseweb="select"] > div { background-color: #FFFFFF !important; color: #31333F !important; border: 1px solid #D3D3D3 !important; }
                div[data-baseweb="select"] * { color: #31333F !important; }
                label { color: #31333F !important; }
                
                button[data-baseweb="tab"] { color: #555555 !important; font-weight: 500 !important; }
                button[data-baseweb="tab"] p { color: #555555 !important; } 
                button[data-baseweb="tab"][aria-selected="true"] { border-color: #FF4B4B !important; font-weight: 700 !important; }
                button[data-baseweb="tab"][aria-selected="true"] p { color: #FF4B4B !important; }
                
                div[data-testid="stTextInput"], 
                div[data-testid="stTextInput"] > div, 
                div[data-testid="stTextInput"] div[data-baseweb="base-input"],
                div[data-testid="stTextInput"] div[data-baseweb="input"] { 
                    background-color: #FFFFFF !important; 
                    background: #FFFFFF !important;
                    border: 1px solid #D3D3D3 !important; 
                    color: #31333F !important;
                }
                
                div[data-testid="stTextInput"] input { 
                    color: #31333F !important; 
                    background-color: #FFFFFF !important;
                    background: #FFFFFF !important;
                    -webkit-text-fill-color: #31333F !important;
                }
                
                div[data-testid="stTextInput"] input::placeholder {
                    color: #757575 !important;
                    opacity: 1 !important;
                }
                
                div[data-testid="stMetricLabel"] p, div[data-testid="stMetricValue"] { color: #31333F !important; }
                
                .stApp button { 
                    background-color: #F0F2F6 !important; 
                    border: 1px solid #D3D3D3 !important; 
                }
                .stApp button p { 
                    color: #31333F !important; 
                    font-weight: 600 !important;
                }
                .stApp button:hover {
                    background-color: #E4E6EA !important;
                    border-color: #B0B3B8 !important;
                }
                </style>
            """, unsafe_allow_html=True)

        st.divider()
        st.write("⚙️ **App Administration**")
        
        if st.button("Clear App Cache", key="sidebar_clear_cache"):
            st.cache_data.clear()
            st.toast("Cache cleared!")
            
        if st.button("Rerun App Session", key="sidebar_rerun"):
            st.rerun()
            
        st.caption("T Fragrances POS v1.0.0")




