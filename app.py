import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

st.set_page_config(page_title="Trade Park CRM", layout="wide")
st.title("💄 💊 Trade Park LLC - Sales & Inventory CRM")

# Paths fixed relative to this script, not the working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_CSV = os.path.join(BASE_DIR, "products.csv")
CLIENTS_CSV = os.path.join(BASE_DIR, "clients.csv")
INTERACTIONS_CSV = os.path.join(BASE_DIR, "interactions.csv")

PRODUCT_COLS = ['SKU', 'Product Name', 'Category', 'Price', 'Stock', 'Expiry']
CLIENT_COLS = ['Client Name', 'Type', 'Contact', 'Status', 'Last Contact']
INTERACTION_COLS = ['Client Name', 'Date', 'Notes', 'Next Follow-up']
CATEGORIES = ["Cosmetics - Skin Care", "Cosmetics - Makeup", "Supplements - Vitamins", "Supplements - Protein"]
CLIENT_TYPES = ["Distributor", "Pharmacy Chain", "Gym/Wellness Center", "Direct Consumer"]
STATUSES = ["Lead", "Negotiation", "Active Customer", "Inactive"]

for path, cols in [
    (PRODUCTS_CSV, PRODUCT_COLS),
    (CLIENTS_CSV, CLIENT_COLS),
    (INTERACTIONS_CSV, INTERACTION_COLS),
]:
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False)


@st.cache_data
def load_products():
    try:
        return pd.read_csv(PRODUCTS_CSV)
    except Exception:
        return pd.DataFrame(columns=PRODUCT_COLS)


@st.cache_data
def load_clients():
    try:
        return pd.read_csv(CLIENTS_CSV)
    except Exception:
        return pd.DataFrame(columns=CLIENT_COLS)


@st.cache_data
def load_interactions():
    try:
        return pd.read_csv(INTERACTIONS_CSV)
    except Exception:
        return pd.DataFrame(columns=INTERACTION_COLS)


def safe_index(lst, val):
    try:
        return lst.index(val)
    except ValueError:
        return 0


def safe_date(val):
    try:
        return datetime.strptime(str(val), "%Y-%m-%d").date()
    except Exception:
        return date.today()


menu = st.sidebar.radio("Navigation", ["Dashboard", "Products", "Clients", "Interactions"])

# --- DASHBOARD ---
if menu == "Dashboard":
    st.header("📊 Company Overview")
    df_prod = load_products()
    df_clients = load_clients()
    df_inter = load_interactions()

    c1, c2, c3 = st.columns(3)
    c1.metric("Products", len(df_prod))
    c2.metric("Clients", len(df_clients))
    c3.metric("Interactions", len(df_inter))

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Inventory")
        st.dataframe(df_prod, use_container_width=True)
    with c2:
        st.subheader("Clients")
        st.dataframe(df_clients, use_container_width=True)

# --- PRODUCTS ---
elif menu == "Products":
    st.header("📦 Products")
    tab_add, tab_manage = st.tabs(["Add Product", "Manage Products"])

    with tab_add:
        with st.form("add_product"):
            col1, col2 = st.columns(2)
            sku = col1.text_input("SKU Code (e.g., TP-COS-001)")
            name = col2.text_input("Product Name")
            category = st.selectbox("Category", CATEGORIES)
            price = st.number_input("Unit Price ($)", min_value=0.0, format="%.2f")
            stock = st.number_input("Initial Stock", min_value=0, step=1)
            expiry = st.date_input("Expiry Date")
            submitted = st.form_submit_button("Save Product")

            if submitted:
                errors = []
                if not sku.strip():
                    errors.append("SKU Code is required.")
                if not name.strip():
                    errors.append("Product Name is required.")
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    df = load_products()
                    if sku.strip() in df['SKU'].astype(str).values:
                        st.error(f"SKU '{sku.strip()}' already exists.")
                    else:
                        pd.DataFrame(
                            [[sku.strip(), name.strip(), category, price, int(stock), str(expiry)]],
                            columns=PRODUCT_COLS
                        ).to_csv(PRODUCTS_CSV, mode='a', header=False, index=False)
                        load_products.clear()
                        st.success(f"✅ {name.strip()} added.")

    with tab_manage:
        df = load_products()
        if df.empty:
            st.info("No products yet.")
        else:
            options = (df['SKU'].astype(str) + " — " + df['Product Name'].astype(str)).tolist()
            selected = st.selectbox("Select Product", options)
            sku_sel = selected.split(" — ")[0]
            row = df[df['SKU'].astype(str) == sku_sel].iloc[0]

            st.subheader(f"Editing: {row['Product Name']}")
            with st.form("edit_product"):
                new_name = st.text_input("Product Name", value=str(row['Product Name']))
                new_cat = st.selectbox("Category", CATEGORIES, index=safe_index(CATEGORIES, row['Category']))
                new_price = st.number_input("Price ($)", min_value=0.0, value=float(row['Price']), format="%.2f")
                new_stock = st.number_input("Stock", min_value=0, value=int(row['Stock']), step=1)
                new_expiry = st.date_input("Expiry Date", value=safe_date(row['Expiry']))
                save = st.form_submit_button("Save Changes")

                if save:
                    if not new_name.strip():
                        st.error("Product Name is required.")
                    else:
                        df.loc[df['SKU'].astype(str) == sku_sel,
                               ['Product Name', 'Category', 'Price', 'Stock', 'Expiry']] = [
                            new_name.strip(), new_cat, new_price, int(new_stock), str(new_expiry)
                        ]
                        df.to_csv(PRODUCTS_CSV, index=False)
                        load_products.clear()
                        st.success("✅ Product updated.")

            st.divider()
            confirm_del = st.checkbox(f"Confirm deletion of **{row['Product Name']}**")
            if st.button("Delete Product", disabled=not confirm_del, type="primary"):
                df = df[df['SKU'].astype(str) != sku_sel]
                df.to_csv(PRODUCTS_CSV, index=False)
                load_products.clear()
                st.success("Product deleted.")
                st.rerun()

# --- CLIENTS ---
elif menu == "Clients":
    st.header("🤝 Clients")
    tab_add, tab_manage = st.tabs(["Add Client", "Manage Clients"])

    with tab_add:
        with st.form("add_client"):
            c_name = st.text_input("Client/Business Name")
            c_type = st.selectbox("Client Type", CLIENT_TYPES)
            contact = st.text_input("Email / Phone")
            status = st.selectbox("Pipeline Status", STATUSES)
            submitted = st.form_submit_button("Save Client")

            if submitted:
                if not c_name.strip():
                    st.error("Client Name is required.")
                else:
                    df = load_clients()
                    if c_name.strip() in df['Client Name'].astype(str).values:
                        st.error(f"Client '{c_name.strip()}' already exists.")
                    else:
                        pd.DataFrame(
                            [[c_name.strip(), c_type, contact.strip(), status, str(date.today())]],
                            columns=CLIENT_COLS
                        ).to_csv(CLIENTS_CSV, mode='a', header=False, index=False)
                        load_clients.clear()
                        st.success(f"✅ {c_name.strip()} registered.")

    with tab_manage:
        df = load_clients()
        if df.empty:
            st.info("No clients yet.")
        else:
            selected = st.selectbox("Select Client", df['Client Name'].astype(str).tolist())
            row = df[df['Client Name'].astype(str) == selected].iloc[0]

            with st.form("edit_client"):
                new_type = st.selectbox("Client Type", CLIENT_TYPES, index=safe_index(CLIENT_TYPES, row['Type']))
                new_contact = st.text_input("Email / Phone", value=str(row['Contact']))
                new_status = st.selectbox("Pipeline Status", STATUSES, index=safe_index(STATUSES, row['Status']))
                save = st.form_submit_button("Save Changes")

                if save:
                    df.loc[df['Client Name'].astype(str) == selected,
                           ['Type', 'Contact', 'Status']] = [new_type, new_contact.strip(), new_status]
                    df.to_csv(CLIENTS_CSV, index=False)
                    load_clients.clear()
                    st.success("✅ Client updated.")

            st.divider()
            confirm_del = st.checkbox(f"Confirm deletion of **{selected}**")
            if st.button("Delete Client", disabled=not confirm_del, type="primary"):
                df = df[df['Client Name'].astype(str) != selected]
                df.to_csv(CLIENTS_CSV, index=False)
                load_clients.clear()
                st.success("Client deleted.")
                st.rerun()

# --- INTERACTIONS ---
elif menu == "Interactions":
    st.header("📞 Sales Interactions")
    tab_log, tab_history = st.tabs(["Log Interaction", "History"])

    with tab_log:
        df_clients = load_clients()
        if df_clients.empty:
            st.warning("No clients found. Add a client first.")
        else:
            client = st.selectbox("Select Client", df_clients['Client Name'].unique())
            notes = st.text_area("Meeting Notes")
            next_followup = st.date_input("Next Follow-up Date")

            if st.button("Log Interaction"):
                if not notes.strip():
                    st.error("Meeting notes are required.")
                else:
                    pd.DataFrame(
                        [[client, str(date.today()), notes.strip(), str(next_followup)]],
                        columns=INTERACTION_COLS
                    ).to_csv(INTERACTIONS_CSV, mode='a', header=False, index=False)
                    load_interactions.clear()

                    df_clients.loc[df_clients['Client Name'] == client, 'Last Contact'] = str(date.today())
                    df_clients.to_csv(CLIENTS_CSV, index=False)
                    load_clients.clear()

                    st.success(f"✅ Interaction with {client} logged.")

    with tab_history:
        df_inter = load_interactions()
        if df_inter.empty:
            st.info("No interactions logged yet.")
        else:
            df_clients_f = load_clients()
            filter_client = "All"
            if not df_clients_f.empty:
                filter_client = st.selectbox("Filter by Client", ["All"] + df_clients_f['Client Name'].tolist())
            if filter_client != "All":
                df_inter = df_inter[df_inter['Client Name'] == filter_client]
            st.dataframe(df_inter.sort_values('Date', ascending=False), use_container_width=True)
