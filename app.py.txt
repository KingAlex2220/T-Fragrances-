import streamlit as st
import pandas as pd
import random
import datetime

# --- CONFIGURATION & SESSION STATE INITIALIZATION ---
st.set_page_config(page_title="T Fragrances - App Suite", page_icon="✨", layout="wide")

# Initialize persistent mock database for orders if it doesn't exist
if "order_db" not in st.session_state:
    st.session_state.order_db = pd.DataFrame(columns=[
        "Order ID", "Timestamp", "Customer Name", "Category", 
        "Product Code", "Scent Name", "Payment Method", "Total Paid", "Status"
    ])

# Initialize user cart
if "cart" not in st.session_state:
    st.session_state.cart = None

# --- MOCK DATA GENERATION (Mirroring Master Catalogs) ---
men_scents = [
    {"code": "T Fragrances Your Scent #48E", "designer": "CREED", "scent": "AVENTUS"},
    {"code": "T Fragrances Your Scent #134G", "designer": "PACO RABANNE", "scent": "INVICTUS"},
    {"code": "T Fragrances Your Scent #17C", "designer": "ARMANI", "scent": "ACQUA DI GIO"},
    {"code": "T Fragrances Your Scent #155N", "designer": "TOM FORD", "scent": "OMBRE LEATHER"}
]

women_scents = [
    {"code": "T Fragrances Your Scent #11A", "designer": "ARIANA GRANDE", "scent": "CLOUD"},
    {"code": "T Fragrances Your Scent #15A", "designer": "CHANEL", "scent": "COCO MADEMOISELLE"},
    {"code": "T Fragrances Your Scent #40A", "designer": "CAROLINA HERRERA", "scent": "GOOD GIRL"}
]

home_scents = [
    {"code": "T Fragrances Home Scent #2", "designer": "HOUSE BLEND", "scent": "COTTON CANDY"},
    {"code": "T Fragrances Home Scent #12", "designer": "HOUSE BLEND", "scent": "CUCUMBER MELON"},
    {"code": "T Fragrances Home Scent #45", "designer": "HOUSE BLEND", "scent": "HOLY SAGE"}
]

# Price Sheet
PRICE_MAP = {"Men's Fragrances": 45.00, "Women's Fragrances": 45.00, "Home Scents": 30.00}

# --- HEADER & BRANDING ---
st.markdown("<h1 style='text-align: center; color: #1E293B;'>T FRAGRANCES</h1>", unsafe_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #64748B;'>Designer Quality | 100% Oil-Based | Reimagined Luxury</p>", unsafe_html=True)
st.markdown("---")

# Navigation Tabs
tab_shop, tab_track, tab_admin = st.tabs(["🛒 Customer Storefront & POS", "📦 Track Your Purchase", "🛡️ Admin Order Operations"])

# ==========================================
# TAB 1: CUSTOMER STOREFRONT & DIGITAL POS
# ==========================================
with tab_shop:
    st.subheader("Digital Point of Sale (POS) Checkout")
    
    col_input, col_summary = st.columns([2, 1])
    
    with col_input:
        st.markdown("### 1. Select Product Category")
        category = st.radio("What are we shopping for today?", ["Men's Fragrances", "Women's Fragrances", "Home Scents"], horizontal=True)
        
        # Determine product list based on category
        if category == "Men's Fragrances":
            active_list = men_scents
        elif category == "Women's Fragrances":
            active_list = women_scents
        else:
            active_list = home_scents
            
        options_format = [f"{item['code']} - Inspired by {item['designer']} ({item['scent']})" for item in active_list]
        
        st.markdown("### 2. Choose Scent")
        selected_option = st.selectbox("Locate your alphanumeric matching code:", options_format)
        
        # Extract selected item info
        selected_index = options_format.index(selected_option)
        chosen_item = active_list[selected_index]
        
        st.markdown("### 3. Customer & Payment Details")
        cust_name = st.text_input("Customer Full Name:", placeholder="Alex Thompson")
        pay_method = st.selectbox("Select Digital Payment Method:", ["Apple Pay", "Venmo", "Cash App", "Credit/Debit Card", "Zelle"])
        
        if st.button("Calculate Order Summary", type="primary"):
            if cust_name.strip() == "":
                st.error("Please enter a customer name to proceed.")
            else:
                st.session_state.cart = {
                    "Customer Name": cust_name,
                    "Category": category,
                    "Product Code": chosen_item["code"],
                    "Scent Name": chosen_item["scent"],
                    "Payment Method": pay_method,
                    "Price": PRICE_MAP[category]
                }

    with col_summary:
        st.markdown("### 🧾 Live Invoice")
        if st.session_state.cart is not None:
            cart = st.session_state.cart
            st.info(f"**Ready for Payment Processing via {cart['Payment Method']}**")
            
            st.markdown(f"**Customer:** {cart['Customer Name']}")
            st.markdown(f"**Item Selection:** {cart['Product Code']}")
            st.markdown(f"**Scent Profile:** {cart['Scent Name']}")
            st.markdown("---")
            st.markdown(f"### **Total Due: ${cart['Price']:.2f}**")
            st.caption("100% pure oil concentration formulation.")
            
            if st.button("Confirm Digital Payment & Process Order"):
                # Generate unique Order ID
                order_id = f"TF-{random.randint(10000, 99999)}"
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Append to persistent DataFrame
                new_order = pd.DataFrame([{
                    "Order ID": order_id,
                    "Timestamp": timestamp,
                    "Customer Name": cart["Customer Name"],
                    "Category": cart["Category"],
                    "Product Code": cart["Product Code"],
                    "Scent Name": cart["Scent Name"],
                    "Payment Method": cart["Payment Method"],
                    "Total Paid": cart["Price"],
                    "Status": "Processing (Oil Ratios Verifying)"
                }])
                
                st.session_state.order_db = pd.concat([st.session_state.order_db, new_order], ignore_index=True)
                st.success(f"🎉 Payment successful via {cart['Payment Method']}! Order Created.")
                st.balloons()
                
                # Show receipt copy
                st.code(f"""
                ===================================
                           T FRAGRANCES
                ===================================
                ORDER ID: {order_id}
                DATE: {timestamp}
                CLIENT: {cart['Customer Name']}
                -----------------------------------
                CODE: {cart['Product Code']}
                SCENT: {cart['Scent Name']}
                BASE: 100% Pure Oil Formula
                -----------------------------------
                PAID VIA: {cart['Payment Method']}
                TOTAL: ${cart['Price']:.2f}
                ===================================
                Thank you for choosing reimagined luxury!
                """)
                
                # Clear temporary cart state
                st.session_state.cart = None
        else:
            st.write("No active transaction items calculated yet.")

# ==========================================
# TAB 2: CUSTOMER PURCHASE TRACKING PORTAL
# ==========================================
with tab_track:
    st.subheader("Track Your Scent Order")
    st.write("Enter your unique tracking receipt reference number (`TF-XXXXX`) to check your pipeline routing status.")
    
    search_id = st.text_input("Order ID:", placeholder="TF-12345").strip()
    
    if st.button("Search Pipeline Status"):
        db = st.session_state.order_db
        match = db[db["Order ID"] == search_id]
        
        if not match.empty:
            order_info = match.iloc[0]
            st.markdown("#### Order Blueprint Record Found:")
            
            # Status tracking stepper UI card
            st.metric(label="Current Production Status", value=order_info["Status"])
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.write(f"**Customer Name:** {order_info['Customer Name']}")
                st.write(f"**Product Mapping:** {order_info['Product Code']}")
                st.write(f"**Scent Profile:** {order_info['Scent Name']}")
            with col_t2:
                st.write(f"**Order Log Time:** {order_info['Timestamp']}")
                st.write(f"**Funding Vector:** {order_info['Payment Method']}")
                st.write(f"**Amount Handled:** ${order_info['Total Paid']:.2f}")
        else:
            st.error("No record found matching that Order ID. Please check your spelling or contact support.")

# ==========================================
# TAB 3: ADMIN ORDER OPERATIONS & MONITORING
# ==========================================
with tab_admin:
    st.subheader("Secure Operational Dashboard")
    st.caption("Internal fulfillment tools to update batch status logs and check payment performance metrics.")
    
    db = st.session_state.order_db
    
    if db.empty:
        st.info("No incoming orders logged in this instance session yet.")
    else:
        # Display high level tracking metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Income Volume", f"${db['Total Paid'].sum():.2f}")
        col_m2.metric("Total Bottles Ordered", len(db))
        col_m3.metric("Pending Formulations", len(db[db["Status"] != "Shipped / Picked Up"]))
        
        st.markdown("### Master Inflow Pipeline Log")
        st.dataframe(db, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### Change Scent Fulfillment Progress")
        
        col_up1, col_up2 = st.columns(2)
        with col_up1:
            selected_id_to_edit = st.selectbox("Target Order ID to modify:", db["Order ID"].unique())
        with col_up2:
            new_status_val = st.selectbox("Updated Pipeline Status:", [
                "Processing (Oil Ratios Verifying)",
                "Batch Steeping & Blending",
                "Quality Inspection Completed",
                "Out for Courier Delivery",
                "Shipped / Picked Up"
            ])
            
        if st.button("Commit Status Transition Update"):
            st.session_state.order_db.loc[st.session_state.order_db["Order ID"] == selected_id_to_edit, "Status"] = new_status_val
            st.success(f"Status for {selected_id_to_edit} updated to: '{new_status_val}'")
            st.rerun()
