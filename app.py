import os
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="T-Fragrances Store", page_icon="🛍️", layout="wide"
)

# App Header
st.title("T-Fragrances Store")
st.markdown("### 100% Oil-Based Designer Impressions — **$45**")


# Function to load catalog files safely
def load_catalog(filename):
  if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as f:
      return f.read()
  return "Catalog data loading..."


# Sidebar - Store Navigation & QR Codes
st.sidebar.markdown("---")
st.sidebar.subheader("📲 Scan to Order & Pay")

# Main Catalog / Store QR Code
if os.path.exists("qr_code.png"):
  st.sidebar.image(
      "qr_code.png", caption="Scan to open T-Fragrances Store", use_container_width=True
  )
else:
  st.sidebar.info("Place your QR image file as 'qr_code.png' in your repository.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💳 Quick Payment Options")

# Creating tabs for smooth switching between payment apps in the sidebar
pay_tab1, pay_tab2, pay_tab3 = st.sidebar.tabs(["Cash App", "Venmo", "Zelle"])

with pay_tab1:
  st.markdown("**Jameka Howell**")
  st.markdown("`$JaMekaHowell`")
  if os.path.exists("cashapp_qr.png"):
    st.image("cashapp_qr.png", use_container_width=True)
  else:
    st.info("Upload cashapp_qr.png to root directory")

with pay_tab2:
  st.markdown("**Jameka Hatton**")
  st.markdown("`@Jameka-Hatton`")
  if os.path.exists("venmo_qr.png"):
    st.image("venmo_qr.png", use_container_width=True)
  else:
    st.info("Upload venmo_qr.png to root directory")

with pay_tab3:
  st.markdown("**Alexander Thompson**")
  st.markdown("`***-***-4196`")
  if os.path.exists("zelle_qr.png"):
    st.image("zelle_qr.png", use_container_width=True)
  else:
    st.info("Upload zelle_qr.png to root directory")

# Main Storefront Layout & Filters
st.sidebar.markdown("---")
collection_filter = st.sidebar.radio("Collection Filter", ["All", "Men", "Women"])

# Load Catalog Data
home_catalog = load_catalog("home_catalog.txt")
mens_catalog = load_catalog("mens_catalog.txt")

# Display content based on filter selection
if collection_filter == "All":
  st.markdown("### Featured Collection")
  st.write(home_catalog)
elif collection_filter == "Men":
  st.markdown("### Men's Impressions")
  st.write(mens_catalog)
else:
  st.markdown("### Women's Impressions")
  st.info("Women's catalog inventory coming soon!")

# Shopping Bag Summary Section
st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Shopping Bag Summary")
st.sidebar.text("Items in Bag: 0")
st.sidebar.text("Total: $0.00")
