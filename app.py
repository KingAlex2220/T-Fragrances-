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
# DATABASE SETUP & AUTO-MIGRATION
# ==========================================
DB_FILE = "t_fragrances.db"
DEFAULT_STOCK_PER_ITEM = 5


def init_db():
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()

  # Create Orders Table
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

  # Create Inventory Table
  c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            item_name TEXT,
            stock_level INTEGER,
            initial_stock INTEGER
        )
    """)

  # Create Gift Cards Table (Safe check included)
  c.execute("""
        CREATE TABLE IF NOT EXISTS gift_cards (
            code TEXT PRIMARY KEY,
            initial_value REAL,
            current_balance REAL,
            purchaser_name TEXT,
            recipient_email TEXT,
            status TEXT,
            created_date TEXT
        )
    """)

  conn.commit()
  conn.close()


init_db()

# ==========================================
# CATALOG & DISCOUNTS
# ==========================================
DISCLAIMER_TEXT = (
    "TF Fragrances offers proprietary, independently formulated scents"
    " inspired by popular fragrance profiles. Any reference to scent families or"
    " style impressions is strictly for descriptive purposes to give"
    " customers an idea of the olfactory notes."
)

ALLERGY_DISCLAIMER_TEXT = (
    "⚠️ ALLERGY & SKIN SENSITIVITY NOTICE: T Fragrances products contain"
    " concentrated fragrance oils, essential oils, and aromatic compounds."
    " Please perform a patch test prior to full application."
)

FRAGRANCE_CATALOG = [
    {
        "id": "sig_m1",
        "name": "No 1 — Savage Spirit Blend",
        "gender": "Men",
        "category": "Signature Blend",
        "price": 45.0,
        "notes": "Inspired by Sauvage profile: Bergamot, pepper, ambroxan.",
    },
    {
        "id": "sig_m4",
        "name": "No 4 — Monarch Creed (Aventus Blend)",
        "gender": "Men",
        "category": "Signature Blend",
        "price": 45.0,
        "notes": (
            "Inspired by Aventus profile: Smoky pineapple, birchwood, oakmoss."
        ),
    },
    {
        "id": "sig_w2",
        "name": "No 2 — Good Girl Blend",
        "gender": "Women",
        "category": "Signature Blend",
        "price": 45.0,
        "notes": (
            "Inspired by Good Girl profile: Tuberose, roasted tonka bean, cocoa."
        ),
    },
    {
        "id": "sig_w3",
        "name": "No 3 — Crystal Rouge 540 Blend",
        "gender": "Women",
        "category": "Signature Blend",
        "price": 45.0,
        "notes": (
            "Inspired by Baccarat Rouge 540 profile: Jasmine, saffron, ambergris."
        ),
    },
]


def sync_inventory_defaults():
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()
  for item in FRAGRANCE_CATALOG:
    c.execute("SELECT stock_level FROM inventory WHERE item_id = ?", (item["id"],))
    if not c.fetchone():
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


# Helper Functions
def get_current_30_day_cycle():
  now = datetime.now()
  start_of_year = datetime(now.year, 1, 1)
  days_passed = (now - start_of_year).days
  cycle_num = (days_passed // 30) + 1
  return f"CYCLE-{now.year}-30D-{cycle_num:02d}"


def create_gift_card(code, value, purchaser, recipient):
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()
  created_date = datetime.now().strftime("%Y-%m-%d")
  c.execute(
      """
        INSERT OR REPLACE INTO gift_cards (code, initial_value, current_balance, purchaser_name, recipient_email, status, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
      (code, value, value, purchaser, recipient, "Active", created_date),
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


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "cart" not in st.session_state:
  st.session_state.cart = {}
if "applied_gift_card" not in st.session_state:
  st.session_state.applied_gift_card = None
if "gift_card_discount" not in st.session_state:
  st.session_state.gift_card_discount = 0.0


def add_to_cart(item_id):
  st.session_state.cart[item_id] = st.session_state.cart.get(item_id, 0) + 1
  st.toast("Added to bag!", icon="🛍️")


# ==========================================
# SIDEBAR BAG & TOTALS
# ==========================================
st.sidebar.title("✨ T Fragrances")
total_qty = sum(st.session_state.cart.values())
raw_subtotal = sum(
    next(item["price"] for item in FRAGRANCE_CATALOG if item["id"] == i_id) * qty
    for i_id, qty in st.session_state.cart.items()
)

discount = 0.0
if raw_subtotal >= 100.0:
  discount = 0.20
elif total_qty >= 3:
  discount = 0.15
elif total_qty == 2:
  discount = 0.10

subtotal_after_volume = raw_subtotal * (1 - discount)
final_subtotal = max(
    0.0, subtotal_after_volume - st.session_state.gift_card_discount
)

st.sidebar.subheader("🛒 Shopping Bag")
st.sidebar.write(f"**Items:** {total_qty}")
if st.session_state.applied_gift_card:
  st.sidebar.write(
      f"**Gift Card ({st.session_state.applied_gift_card}):**"
      f" -${st.session_state.gift_card_discount:.2f}"
  )
st.sidebar.subheader(f"Total: ${final_subtotal:.2f}")

# ==========================================
# MAIN TABS (INCLUDING GIFT CARDS)
# ==========================================
tabs = st.tabs([
    "✨ Signature Blends",
    "🎁 Gift Cards & Credit",
    "🛒 Checkout & Invoice",
])

with tabs[0]:
  st.header("Signature Blends ($45.00)")
  for item in FRAGRANCE_CATALOG:
    cols = st.columns([3, 1])
    with cols[0]:
      st.markdown(f"### {item['name']}")
      st.write(item["notes"])
    with cols[1]:
      st.write(f"**${item['price']:.2f}**")
      st.button(
          "Add to Bag", key=f"add_{item['id']}", on_click=add_to_cart, args=(item["id"],)
      )
    st.markdown("---")

with tabs[1]:
  st.header("🎁 Digital Gift Cards & Store Credit")
  st.markdown(
      "Purchase a store gift card or redeem an active code toward your order."
  )

  gc_tab1, gc_tab2 = st.tabs(["Purchase Gift Card", "Redeem Code"])

  with gc_tab1:
    with st.form("purchase_gc_form"):
      gc_purchaser = st.text_input("Your Name *")
      gc_recipient = st.text_input("Recipient Email or Name *")
      gc_value = st.number_input(
          "Gift Card Amount ($)", min_value=10.0, value=45.0, step=5.0
      )
      gc_submit = st.form_submit_button("Generate Gift Card Code")

      if gc_submit:
        if not (gc_purchaser and gc_recipient):
          st.error("Please fill in both names.")
        else:
          random_str = "".join(
              random.choices(string.ascii_uppercase + string.digits, k=6)
          )
          gc_code = f"TF-GC-{random_str}"
          create_gift_card(gc_code, gc_value, gc_purchaser, gc_recipient)
          st.success("🎉 Gift Card Generated Successfully!")
          st.info(f"**Code:** `{gc_code}` | **Value:** ${gc_value:.2f}")

  with gc_tab2:
    with st.form("redeem_gc_form"):
      entered_code = st.text_input(
          "Enter Gift Card Code (e.g., TF-GC-XXXXXX)"
      ).strip()
      redeem_submit = st.form_submit_button("Apply to Order")

      if redeem_submit:
        card_data = get_gift_card(entered_code.upper())
        if not card_data:
          st.error("Invalid gift card code.")
        else:
          balance = card_data[2]
          status = card_data[5]
          if status != "Active" or balance <= 0:
            st.warning("This gift card has a zero balance or is inactive.")
          else:
            st.session_state.applied_gift_card = entered_code.upper()
            st.session_state.gift_card_discount = balance
            st.success(
                f"✅ Gift card applied! Credit Available: ${balance:.2f}"
            )
            st.rerun()

with tabs[2]:
  st.header("🧾 Checkout & Summary")
  if not st.session_state.cart:
    st.info("Your bag is empty.")
  else:
    st.write(f"**Raw Subtotal:** ${raw_subtotal:.2f}")
    if discount >  0:
      st.write(f"**Volume Discount:** -${raw_subtotal * discount:.2f}")
    if st.session_state.applied_gift_card:
      st.write(
          f"**Gift Card Credit:** -${st.session_state.gift_card_discount:.2f}"
      )
    st.markdown(f"### **Final Total: ${final_subtotal:.2f}**")

    if st.button("Complete Order Test"):
      # Clear gift card balance in DB if fully used
      if st.session_state.applied_gift_card:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "UPDATE gift_cards SET current_balance = 0, status = 'Redeemed'"
            " WHERE code = ?",
            (st.session_state.applied_gift_card,),
        )
        conn.commit()
        conn.close()

      st.success("Order processed successfully!")
      st.session_state.cart = {}
      st.session_state.applied_gift_card = None
      st.session_state.gift_card_discount = 0.0
      st.rerun()
