# Trade Park LLC - Sales & Inventory CRM

A Streamlit-based CRM system for Trade Park LLC to manage cosmetics and supplements inventory, client relationships, and sales interactions.

## Features

- **Dashboard**: View all products and clients at a glance
- **Product Management**: Add and track cosmetics and supplements with SKU codes, pricing, stock levels, and expiry dates
- **Client Management**: Register and manage distributors, pharmacy chains, gyms, wellness centers, and direct consumers
- **Interaction Logging**: Track sales calls and meetings with clients

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## Data Storage

The application uses CSV files for data persistence:
- `products.csv` - Product inventory
- `clients.csv` - Client information
