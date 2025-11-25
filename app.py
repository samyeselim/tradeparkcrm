import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Trade Park CRM", layout="wide")
st.title("💄 💊 Trade Park LLC - Sales & Inventory CRM")

# --- FILE HANDLING (Simple CSV Database) ---
if not os.path.exists('products.csv'):
    pd.DataFrame(columns=['SKU', 'Product Name', 'Category', 'Price', 'Stock', 'Expiry']).to_csv('products.csv', index=False)
if not os.path.exists('clients.csv'):
    pd.DataFrame(columns=['Client Name', 'Type', 'Contact', 'Status', 'Last Contact']).to_csv('clients.csv', index=False)

# --- SIDEBAR NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["Dashboard", "Add New SKU", "Add New Client", "Log Interaction"])

# --- PAGE: DASHBOARD ---
if menu == "Dashboard":
    st.header("📊 Company Overview")
    
    # Load Data
    df_prod = pd.read_csv('products.csv')
    df_clients = pd.read_csv('clients.csv')

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Inventory (Cosmetics & Supplements)")
        st.dataframe(df_prod, use_container_width=True)
        
    with col2:
        st.subheader("Client List")
        st.dataframe(df_clients, use_container_width=True)

# --- PAGE: ADD SKU ---
elif menu == "Add New SKU":
    st.header("📦 Add Product to Catalog")
    with st.form("sku_form"):
        col1, col2 = st.columns(2)
        sku_code = col1.text_input("SKU Code (e.g., TP-COS-001)")
        prod_name = col2.text_input("Product Name")
        category = st.selectbox("Category", ["Cosmetics - Skin Care", "Cosmetics - Makeup", "Supplements - Vitamins", "Supplements - Protein"])
        price = st.number_input("Unit Price ($)", min_value=0.0)
        stock = st.number_input("Initial Stock", min_value=0, step=1)
        expiry = st.date_input("Expiry Date")
        
        submitted = st.form_submit_button("Save Product")
        if submitted:
            new_data = pd.DataFrame([[sku_code, prod_name, category, price, stock, expiry]], 
                                    columns=['SKU', 'Product Name', 'Category', 'Price', 'Stock', 'Expiry'])
            new_data.to_csv('products.csv', mode='a', header=False, index=False)
            st.success(f"Success! {prod_name} added to database.")

# --- PAGE: ADD CLIENT ---
elif menu == "Add New Client":
    st.header("🤝 Register New Client")
    with st.form("client_form"):
        c_name = st.text_input("Client/Business Name")
        c_type = st.selectbox("Client Type", ["Distributor", "Pharmacy Chain", "Gym/Wellness Center", "Direct Consumer"])
        contact = st.text_input("Email / Phone")
        status = st.selectbox("Pipeline Status", ["Lead", "Negotiation", "Active Customer", "Inactive"])
        
        submitted = st.form_submit_button("Save Client")
        if submitted:
            new_data = pd.DataFrame([[c_name, c_type, contact, status, str(datetime.now().date())]], 
                                    columns=['Client Name', 'Type', 'Contact', 'Status', 'Last Contact'])
            new_data.to_csv('clients.csv', mode='a', header=False, index=False)
            st.success(f"Client {c_name} registered.")

# --- PAGE: LOG INTERACTION ---
elif menu == "Log Interaction":
    st.header("📞 Log Sales Call / Meeting")
    df_clients = pd.read_csv('clients.csv')
    
    if not df_clients.empty:
        selected_client = st.selectbox("Select Client", df_clients['Client Name'].unique())
        notes = st.text_area("Meeting Notes")
        next_step = st.date_input("Next Follow-up Date")
        
        if st.button("Update Log"):
            st.info("Interaction logged (This would connect to a history database in the full version).")
    else:
        st.warning("No clients found. Please add a client first.")