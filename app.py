from datetime import datetime
import os
import sqlite3
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
DEFAULT_STOCK_PER_ITEM = 5  # Default 5 bottles per scent


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
            notes TEXT
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

  c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            item_name TEXT,
            stock_level INTEGER,
            initial_stock INTEGER
        )
    """)

  conn.commit()
  conn.close()


init_db()

# ==========================================
# GLOBAL DISCLAIMERS & CATALOG DATA
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
    # --- MEN'S COLLECTION (30) ---
    {
        "id": "m01",
        "name": "Savage Spirit Blend",
        "gender": "Men",
        "category": "Fresh & Spicy",
        "price": 45.0,
        "notes": (
            "Inspired by Sauvage profile — Crisp bergamot, pepper, and rich"
            " ambroxan."
        ),
        "image_url": "savage_spirit.png",
    },
    {
        "id": "m02",
        "name": "Monarch Creed",
        "gender": "Men",
        "category": "Fruity & Woody",
        "price": 45.0,
        "notes": (
            "Inspired by Aventus profile — Smoky pineapple, birchwood, and"
            " oakmoss."
        ),
        "image_url": None,
    },
    {
        "id": "m03",
        "name": "Azure Night",
        "gender": "Men",
        "category": "Woody & Aromatic",
        "price": 45.0,
        "notes": (
            "Inspired by Bleu de Chanel profile — Fresh grapefruit, incense,"
            " and cedarwood."
        ),
        "image_url": None,
    },
    {
        "id": "m04",
        "name": "Oceanic Drift",
        "gender": "Men",
        "category": "Aquatic & Fresh",
        "price": 45.0,
        "notes": (
            "Inspired by Acqua Di Gio profile — Marine minerals, mandarin, and"
            " ocean breeze."
        ),
        "image_url": None,
    },
    {
        "id": "m05",
        "name": "Smoky Reserve",
        "gender": "Men",
        "category": "Warm & Gourmand",
        "price": 45.0,
        "notes": (
            "Inspired by Tobacco Vanille profile — Rich tobacco leaf, sweet"
            " vanilla, and spices."
        ),
        "image_url": None,
    },
    {
        "id": "m06",
        "name": "Sailor's Pride",
        "gender": "Men",
        "category": "Oriental & Fresh",
        "price": 45.0,
        "notes": (
            "Inspired by Le Male profile — Classic mint, lavender, and warm tonka"
            " bean."
        ),
        "image_url": None,
    },
    {
        "id": "m07",
        "name": "Crimson Rush",
        "gender": "Men",
        "category": "Spicy & Woody",
        "price": 45.0,
        "notes": (
            "Inspired by Spicebomb profile — Fiery red saffron, fresh"
            " grapefruit, and redwood."
        ),
        "image_url": None,
    },
    {
        "id": "m08",
        "name": "Gilded Leather",
        "gender": "Men",
        "category": "Woody Leather",
        "price": 45.0,
        "notes": (
            "Inspired by Tuscan Leather profile — Warm lavender, Italian lemon,"
            " and cedarwood."
        ),
        "image_url": None,
    },
    {
        "id": "m09",
        "name": "Metallic Citrus",
        "gender": "Men",
        "category": "Fresh Citrus",
        "price": 45.0,
        "notes": (
            "Inspired by Chrome Legend profile — Crisp green apple, bergamot,"
            " and warm amber."
        ),
        "image_url": None,
    },
    {
        "id": "m10",
        "name": "Empire Night",
        "gender": "Men",
        "category": "Aromatic Spice",
        "price": 45.0,
        "notes": (
            "Inspired by Playboy New York profile — Fresh lime, crushed black"
            " pepper, and tonka."
        ),
        "image_url": None,
    },
    {
        "id": "m11",
        "name": "Capital Gold",
        "gender": "Men",
        "category": "Sweet Spice",
        "price": 45.0,
        "notes": (
            "Inspired by 1 Million profile — Blood mandarin, cinnamon, and warm"
            " leather."
        ),
        "image_url": None,
    },
    {
        "id": "m12",
        "name": "Eternity Code",
        "gender": "Men",
        "category": "Oriental Woody",
        "price": 45.0,
        "notes": (
            "Inspired by Armani Code profile — Lemon zest, star anise, and"
            " smooth leather."
        ),
        "image_url": None,
    },
    {
        "id": "m13",
        "name": "Velvet Oud",
        "gender": "Men",
        "category": "Woody Oriental",
        "price": 45.0,
        "notes": (
            "Inspired by Oud Wood profile — Rare oudwood, sandalwood, and"
            " Sichuan pepper."
        ),
        "image_url": None,
    },
    {
        "id": "m14",
        "name": "Invincible Sport",
        "gender": "Men",
        "category": "Fresh Marine",
        "price": 45.0,
        "notes": (
            "Inspired by Invictus profile — Grapefruit, sea salt, and bay leaf"
            " accord."
        ),
        "image_url": None,
    },
    {
        "id": "m15",
        "name": "Night Hero",
        "gender": "Men",
        "category": "Ambery Spice",
        "price": 45.0,
        "notes": (
            "Inspired by Wanted by Night profile — Bergamot, roasted coffee, and"
            " vetiver base."
        ),
        "image_url": None,
    },
    {
        "id": "m16",
        "name": "Urban Legend",
        "gender": "Men",
        "category": "Woody Aquatic",
        "price": 45.0,
        "notes": (
            "Inspired by Light Blue Pour Homme profile — Sea salt, sage, and"
            " driftwood notes."
        ),
        "image_url": None,
    },
    {
        "id": "m17",
        "name": "Bourbon Spice",
        "gender": "Men",
        "category": "Warm Gourmand",
        "price": 45.0,
        "notes": (
            "Inspired by Angels' Share profile — Aged whiskey, cinnamon bark,"
            " and dark amber."
        ),
        "image_url": None,
    },
    {
        "id": "m18",
        "name": "Midnight Nomad",
        "gender": "Men",
        "category": "Oriental Spice",
        "price": 45.0,
        "notes": (
            "Inspired by Ombre Leather profile — Cardamom, leather, and smoked"
            " amber."
        ),
        "image_url": None,
    },
    {
        "id": "m19",
        "name": "Royal Vetiver",
        "gender": "Men",
        "category": "Earthy Woody",
        "price": 45.0,
        "notes": (
            "Inspired by Terre d'Hermes profile — Haitian vetiver, grapefruit,"
            " and pink pepper."
        ),
        "image_url": None,
    },
    {
        "id": "m20",
        "name": "Silver Mountain",
        "gender": "Men",
        "category": "Fresh Green",
        "price": 45.0,
        "notes": (
            "Inspired by Silver Mountain Water profile — Green tea,"
            " blackcurrant, and sandalwood."
        ),
        "image_url": None,
    },
    {
        "id": "m21",
        "name": "Black Amber",
        "gender": "Men",
        "category": "Dark Woody",
        "price": 45.0,
        "notes": (
            "Inspired by Black Orchid profile — Rich amber, patchouli, and dark"
            " cocoa."
        ),
        "image_url": None,
    },
    {
        "id": "m22",
        "name": "Citrus Grove",
        "gender": "Men",
        "category": "Fresh Citrus",
        "price": 45.0,
        "notes": (
            "Inspired by Neroli Portofino profile — Sicilian lemon, neroli, and"
            " cedar."
        ),
        "image_url": None,
    },
    {
        "id": "m23",
        "name": "Desert Sage",
        "gender": "Men",
        "category": "Aromatic Herbal",
        "price": 45.0,
        "notes": (
            "Inspired by Y Le Parfum profile — Wild sage, lavender, and dried"
            " cedar wood."
        ),
        "image_url": None,
    },
    {
        "id": "m24",
        "name": "Vanguard Oud",
        "gender": "Men",
        "category": "Spicy Oud",
        "price": 45.0,
        "notes": (
            "Inspired by Royal Oud profile — Dark leather, cardamom, and smoky"
            " agarwood."
        ),
        "image_url": None,
    },
    {
        "id": "m25",
        "name": "Iron & Oak",
        "gender": "Men",
        "category": "Earthy & Woody",
        "price": 45.0,
        "notes": (
            "Inspired by Legend profile — Oakmoss, clean cedar, and bergamot."
        ),
        "image_url": None,
    },
    {
        "id": "m26",
        "name": "Aromatic Noir",
        "gender": "Men",
        "category": "Woody Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Dior Homme Intense profile — Iris, cardamom, and"
            " sandalwood blend."
        ),
        "image_url": None,
    },
    {
        "id": "m27",
        "name": "Pacific Breeze",
        "gender": "Men",
        "category": "Clean Aquatic",
        "price": 45.0,
        "notes": (
            "Inspired by Aqva Pour Homme profile — Ocean salt, melon, and light"
            " musk."
        ),
        "image_url": None,
    },
    {
        "id": "m28",
        "name": "Titanium Sport",
        "gender": "Men",
        "category": "Fresh Citrus",
        "price": 45.0,
        "notes": (
            "Inspired by Allure Homme Sport profile — Mandarin, pepper, and"
            " white musk."
        ),
        "image_url": None,
    },
    {
        "id": "m29",
        "name": "Equestrian Red",
        "gender": "Men",
        "category": "Fruity Spice",
        "price": 45.0,
        "notes": (
            "Inspired by Polo Red profile — Red apple, saffron, and coffee"
            " accord."
        ),
        "image_url": None,
    },
    {
        "id": "m30",
        "name": "Solitude",
        "gender": "Men",
        "category": "Minimalist Wood",
        "price": 45.0,
        "notes": (
            "Inspired by Molecule 01 profile — Iso E Super, cedar, and subtle"
            " amber notes."
        ),
        "image_url": None,
    },
    # --- WOMEN'S COLLECTION (30) ---
    {
        "id": "w01",
        "name": "Crystal Rouge 540",
        "gender": "Women",
        "category": "Amber & Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Baccarat Rouge 540 profile — Jasmine, saffron,"
            " cedarwood, and ambergris."
        ),
        "image_url": None,
    },
    {
        "id": "w02",
        "name": "Midnight Vanilla",
        "gender": "Women",
        "category": "Warm Gourmand",
        "price": 45.0,
        "notes": (
            "Inspired by Black Opium profile — Rich black coffee, white"
            " flowers, and sweet vanilla."
        ),
        "image_url": None,
    },
    {
        "id": "w03",
        "name": "Stiletto Velvet",
        "gender": "Women",
        "category": "Sweet Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Good Girl profile — Tuberose, roasted tonka bean, and"
            " cocoa."
        ),
        "image_url": None,
    },
    {
        "id": "w04",
        "name": "Heavenly Dream",
        "gender": "Women",
        "category": "Gourmand Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Cloud profile — Coconut cream, lavender, and praline"
            " sweet musk."
        ),
        "image_url": None,
    },
    {
        "id": "w05",
        "name": "Golden Blossom",
        "gender": "Women",
        "category": "Classic Floral",
        "price": 45.0,
        "notes": (
            "Inspired by J'adore profile — Ylang-ylang, Damask rose, and"
            " jasmine."
        ),
        "image_url": None,
    },
    {
        "id": "w06",
        "name": "Royal Peony",
        "gender": "Women",
        "category": "Soft Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Delina profile — Lychee, Turkish rose, peony, and"
            " vanilla."
        ),
        "image_url": None,
    },
    {
        "id": "w07",
        "name": "Sweet Cherry Nectar",
        "gender": "Women",
        "category": "Fruity Gourmand",
        "price": 45.0,
        "notes": (
            "Inspired by Lost Cherry profile — Black cherry, bitter almond, and"
            " liquor notes."
        ),
        "image_url": None,
    },
    {
        "id": "w08",
        "name": "Empress Bloom",
        "gender": "Women",
        "category": "Fresh Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Chance Eau Tendre profile — Pink pepper, jasmine"
            " sambac, and white musk."
        ),
        "image_url": None,
    },
    {
        "id": "w09",
        "name": "Nectarine Sunset",
        "gender": "Women",
        "category": "Fruity Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Nectarine Blossom & Honey profile — Sweet nectarine,"
            " peach, and plum blossom."
        ),
        "image_url": None,
    },
    {
        "id": "w10",
        "name": "Gilded Vanilla",
        "gender": "Women",
        "category": "Warm Amber",
        "price": 45.0,
        "notes": (
            "Inspired by Vanilla Sex profile — Madagascar vanilla, orchid, and"
            " warm amber."
        ),
        "image_url": None,
    },
    {
        "id": "w11",
        "name": "Opulent Orchid",
        "gender": "Women",
        "category": "Exotic Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Velvet Orchid profile — Black orchid, rum, and velvety"
            " spices."
        ),
        "image_url": None,
    },
    {
        "id": "w12",
        "name": "Satin Iris",
        "gender": "Women",
        "category": "Powdery Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Iris Poudre profile — Florentine iris, violet leaves,"
            " and soft suede."
        ),
        "image_url": None,
    },
    {
        "id": "w13",
        "name": "Citrus Bloom",
        "gender": "Women",
        "category": "Fresh Citrus",
        "price": 45.0,
        "notes": (
            "Inspired by Coco Mademoiselle profile — Orange blossom, neroli, and"
            " bergamot peel."
        ),
        "image_url": None,
    },
    {
        "id": "w14",
        "name": "Velvet Rose",
        "gender": "Women",
        "category": "Deep Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Velvet Rose & Oud profile — Clove, Damask rose, and"
            " smoky oud wood."
        ),
        "image_url": None,
    },
    {
        "id": "w15",
        "name": "Solar Jasmine",
        "gender": "Women",
        "category": "Bright Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Alien profile — Solar jasmine, cashmere wood, and"
            " white amber."
        ),
        "image_url": None,
    },
    {
        "id": "w16",
        "name": "Blush Bouquet",
        "gender": "Women",
        "category": "Soft Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Miss Dior profile — Peony, green mandarin, and white"
            " musk."
        ),
        "image_url": None,
    },
    {
        "id": "w17",
        "name": "Sugar Petals",
        "gender": "Women",
        "category": "Sweet Gourmand",
        "price": 45.0,
        "notes": (
            "Inspired by Sweet Like Candy profile — Spun sugar, red berries,"
            " and whipped cream."
        ),
        "image_url": None,
    },
    {
        "id": "w18",
        "name": "Amber Seduction",
        "gender": "Women",
        "category": "Warm Spice",
        "price": 45.0,
        "notes": (
            "Inspired by Amber Rouge profile — Amber resins, plum, and warm"
            " cinnamon."
        ),
        "image_url": None,
    },
    {
        "id": "w19",
        "name": "Island Coconut",
        "gender": "Women",
        "category": "Tropical Fresh",
        "price": 45.0,
        "notes": (
            "Inspired by Bronze Goddess profile — Toasted coconut, tiare flower,"
            " and vanilla bean."
        ),
        "image_url": None,
    },
    {
        "id": "w20",
        "name": "Radiant Goddess",
        "gender": "Women",
        "category": "Oriental Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Olympea profile — Salty vanilla, water jasmine, and"
            " ginger lily."
        ),
        "image_url": None,
    },
    {
        "id": "w21",
        "name": "Cozy Cashmere",
        "gender": "Women",
        "category": "Warm & Cozy",
        "price": 45.0,
        "notes": (
            "Inspired by Warm Cashmere profile — Soft cashmere, sandalwood, and"
            " white amber."
        ),
        "image_url": None,
    },
    {
        "id": "w22",
        "name": "Pink Freesia",
        "gender": "Women",
        "category": "Fresh Floral",
        "price": 45.0,
        "notes": (
            "Inspired by English Pear & Freesia profile — King William pear,"
            " white freesia, and patchouli."
        ),
        "image_url": None,
    },
    {
        "id": "w23",
        "name": "Luminous Pearl",
        "gender": "Women",
        "category": "Clean Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Pure Poison profile — White lily, bergamot, and sheer"
            " musk."
        ),
        "image_url": None,
    },
    {
        "id": "w24",
        "name": "Caramel Mist",
        "gender": "Women",
        "category": "Sweet Gourmand",
        "price": 45.0,
        "notes": (
            "Inspired by Cheirosa 62 profile — Warm caramel, salted butter, and"
            " vanilla."
        ),
        "image_url": None,
    },
    {
        "id": "w25",
        "name": "Botanical Garden",
        "gender": "Women",
        "category": "Green Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Gucci Bloom profile — Tuberose, jasmine, and Rangoon"
            " creeper."
        ),
        "image_url": None,
    },
    {
        "id": "w26",
        "name": "Midnight Rose",
        "gender": "Women",
        "category": "Fruity Floral",
        "price": 45.0,
        "notes": (
            "Inspired by Tresor Midnight Rose profile — Raspberry, rose"
            " absolute, and vanilla spice."
        ),
        "image_url": None,
    },
    {
        "id": "w27",
        "name": "Golden Aura",
        "gender": "Women",
        "category": "Warm Amber",
        "price": 45.0,
        "notes": (
            "Inspired by Grand Soir profile — Honey, benzoin resin, and rich"
            " amber."
        ),
        "image_url": None,
    },
    {
        "id": "w28",
        "name": "Wild Blackberry",
        "gender": "Women",
        "category": "Fruity Woody",
        "price": 45.0,
        "notes": (
            "Inspired by Blackberry & Bay profile — Blackberry juice, bay"
            " leaves, and cedarwood."
        ),
        "image_url": None,
    },
    {
        "id": "w29",
        "name": "Heavenly Musk",
        "gender": "Women",
        "category": "Clean Skin Musk",
        "price": 45.0,
        "notes": (
            "Inspired by Glossier You profile — White musk, iris, and subtle"
            " cotton notes."
        ),
        "image_url": None,
    },
    {
        "id": "w30",
        "name": "Elysian Breeze",
        "gender": "Women",
        "category": "Fresh Aquatic",
        "price": 45.0,
        "notes": (
            "Inspired by L'Imperatrice profile — Water mint, water lily, and"
            " cedar."
        ),
        "image_url": None,
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
):
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()
  order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  cycle_id = get_current_30_day_cycle()
  status = "QR Request / Priority Preorder" if is_priority else "Pending Payment"

  c.execute(
      """
        INSERT INTO orders (
            order_date, customer_name, customer_email, customer_phone, 
            shipping_address, items_summary, total_qty, subtotal, 
            discount_applied, final_total, payment_method, status, is_priority, cycle_id, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        " final_total, status, is_priority, cycle_id FROM orders WHERE"
        " customer_email LIKE ? OR customer_phone LIKE ? ORDER BY id DESC",
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


# ==========================================
# SESSION STATE & CART
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
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("✨ T Fragrances")
st.sidebar.caption("50ml Clear Bottle Luxury Impressions")

search_term = st.sidebar.text_input("🔍 Search fragrance catalog...", "").lower()
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
      caption="Scan to open T-Fragrances Store",
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
  st.markdown("`***-***-4196`")
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

final_subtotal = raw_subtotal * (1 - discount)

st.sidebar.write(f"**Items in Bag:** {total_qty}")
if discount > 0:
  st.sidebar.write(f"**Applied Discount:** {discount_label}")
  st.sidebar.write(f"~~Original: ${raw_subtotal:.2f}~~")
st.sidebar.subheader(f"Total: ${final_subtotal:.2f}")

# ==========================================
# MAIN INTERFACE
# ==========================================
st.title("T Fragrances POS & Master Portal")

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
    "🛍️ Browse Catalog",
    "📲 QR Code Request Portal",
    "🛒 Checkout",
    "🔍 Customer Order Lookup",
    "🔒 Master Admin & Inventory",
])

# ------------------------------------------
# TAB 1: BROWSE CATALOG
# ------------------------------------------
with tabs[0]:
  st.caption(
      f"Showing {len(filtered_catalog)} scents | Retail Price: $45.00 each"
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
  st.header("📲 QR Code Impression Request Portal")
  st.info(
      "✨ **Notice:** You are ordering 100% oil-based designer style impressions"
      " of the products you see scanned from the QR code ($45.00 per bottle)."
  )

  with st.form("qr_request_line_form"):
    qr_cust_name = st.text_input("Your Full Name *")
    qr_cust_contact = st.text_input("Email or Phone Number *")
    qr_shipping_address = st.text_input("Delivery / Shipping Address *")

    st.markdown("---")
    st.markdown("### Request Line")
    st.write(
        "Simply type out the name or impression you want to request from the"
        " catalog view, along with the quantity desired."
    )

    qr_item_requests = st.text_area(
        "What impressions would you like to request? (e.g., 2x Savage Spirit"
        " Blend, 1x Crystal Rouge 540) *"
    )
    qr_total_qty = st.number_input(
        "Total Number of Bottles Requested", min_value=1, value=1
    )

    qr_payment_method = st.selectbox(
        "Preferred Settlement Method",
        ["Cash App", "Zelle", "Venmo", "Cash POS (In-Person)"],
    )
    qr_notes = st.text_area("Additional Request Notes / Custom Preferences")

    qr_submit = st.form_submit_button("Submit QR Impression Request")

    if qr_submit:
      if not (qr_cust_name and qr_cust_contact and qr_shipping_address):
        st.error(
            "Please fill in your name, contact details, and shipping address."
        )
      elif not qr_item_requests:
        st.error(
            "Please specify the impressions you want to request from the QR"
            " code."
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
            is_priority=1,  # QR requests default to priority preorder handling
            notes=(
                "QR Code Custom Request Order. Desired Impressions:"
                f" {qr_item_requests}. "
                + (qr_notes if qr_notes else "")
            ),
            cart_items={},
        )

        st.success(
            f"Success! Your request for {qr_total_qty} impression bottle(s) has"
            f" been submitted for {qr_cust_name}."
        )
        st.info(
            f"Please complete your settlement of **${qr_final_total:.2f}** via"
            f" **{qr_payment_method}** using the payment handles in the"
            " sidebar."
        )

# ------------------------------------------
# TAB 3: CHECKOUT
# ------------------------------------------
with tabs[2]:
  st.header("Order Settlement")

  if not st.session_state.cart:
    st.info("Your bag is currently empty.")
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
      st.markdown(f"### Final Subtotal: ${final_subtotal:.2f}")
    with c2:
      if st.button("Clear Bag"):
        st.session_state.cart = {}
        st.rerun()

    st.markdown("---")
    st.subheader("Customer Shipping & Contact Details")

    with st.form("checkout_form"):
      col_a, col_b = st.columns(2)
      with col_a:
        name = st.text_input("Full Name *")
        email = st.text_input("Email Address *")
      with col_b:
        phone = st.text_input("Phone Number *")
        address = st.text_input("Shipping Address *")

      payment_method = st.radio(
          "Settlement Channel",
          ["Cash App", "Zelle", "Venmo", "Cash POS (In-Person)"],
      )
      is_priority = st.checkbox(
          "🔥 Mark as Priority Preorder (Bypasses standard queue for fastest"
          " fulfillment)"
      )
      notes = st.text_area("Special Delivery Instructions / Scent Preferences")

      st.caption("⚠️ **Safety Acknowledgement**")
      allergy_ack = st.checkbox(
          "I acknowledge that I have read the Allergy & Skin Sensitivity"
          " Disclaimer and agree to perform a skin patch test prior to use."
      )

      if st.form_submit_button("Place Order"):
        if not (name and email and phone and address):
          st.error("Please fill in all required customer fields.")
        elif not allergy_ack:
          st.error(
              "Please acknowledge the Safety & Allergy Disclaimer prior to"
              " completing your order."
          )
        else:
          items_str = ", ".join(summary_list)
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
          )
          st.success(f"Order successfully placed for {name}!")
          if is_priority:
            st.warning(
                "⚡ Priority Preorder activated. Production scheduled on"
                " fast-track timeline."
            )
          st.info(
              f"Send total settlement of **${final_subtotal:.2f}** via"
              f" **{payment_method}**."
          )
          st.session_state.cart = {}

# ------------------------------------------
# TAB 4: CUSTOMER ORDER LOOKUP
# ------------------------------------------
with tabs[3]:
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
          if row["is_priority"]:
            st.warning("🔥 Priority Preorder Queue Active")

# ------------------------------------------
# TAB 5: MASTER ADMIN & RESTOCKING TOOL
# ------------------------------------------
with tabs[4]:
  st.header("🔒 Master Admin Database & Restocking Management")
  admin_pwd = st.text_input("Enter Admin Security Password", type="password")

  if admin_pwd == "admin123":
    st.success("Staff Authentication Verified")

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
      st.success("All fragrance stock levels are fully operational.")

    with st.expander("🛠️ Restock Tool — Batch or Single Item Update"):
      stock_col1, stock_col2, stock_col3 = st.columns([2, 1, 1])
      with stock_col1:
        selected_item_id = st.selectbox(
            "Select Fragrance to Restock",
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

    st.subheader("🗓️ Master Order Database & Priority Queue")

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
                "Priority Preorder Processing",
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
