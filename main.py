import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px

# Data Preparation
# Load datasets
purchase_prices = pd.read_csv("data/2017PurchasePricesDec.csv")
# beginning_inventory = pd.read_csv("data/BegInvFINAL12312016.csv")
# ending_inventory = pd.read_csv("data/EndInvFINAL12312016.csv")
invoice_purchases = pd.read_csv("data/InvoicePurchases12312016.csv")
purchases = pd.read_csv("data/PurchasesFINAL12312016.csv")
sales = pd.read_csv("data/SalesFINAL12312016.csv")



# Data Cleaning and Feature Engineering
sales['SalesDate'] = pd.to_datetime(sales['SalesDate'], errors='coerce')
sales = sales.dropna(subset=['SalesDate'])

# Sort by SalesDate
sales = sales.sort_values(by='SalesDate')

purchases['InvoiceDate'] = pd.to_datetime(purchases['InvoiceDate'], errors='coerce')
sales['SalesQuantity'] = pd.to_numeric(sales['SalesQuantity'], errors='coerce')
# Handle missing values
sales.fillna(0, inplace=True)
purchases.fillna(0, inplace=True)

# Model Building / Analysis
# Demand Forecasting (Simple Moving Average)
sales_grouped = sales.groupby('SalesDate')['SalesQuantity'].sum().rolling(window=30, min_periods=1).mean()

# Inventory Optimization (EOQ and Reorder Point Calculation)
lead_time = 14  # assumed lead time in days
avg_daily_demand = sales.groupby('InventoryId')['SalesQuantity'].mean()
std_dev_demand = sales.groupby('InventoryId')['SalesQuantity'].std()
safety_stock = 1.65 * std_dev_demand  # Assuming 95% service level
reorder_point = (avg_daily_demand * lead_time) + safety_stock

# Merge with product descriptions
reorder_data = reorder_point.reset_index()
reorder_data.columns = ['InventoryId', 'ReorderPoint']

reorder_data = reorder_data.merge(sales[['InventoryId', 'Description']].drop_duplicates(), on='InventoryId')

# Deployment / Visualization
st.title("Inventory Analysis Dashboard")

# Sales Trend Visualization
st.subheader("Sales Trend with Moving Average")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(sales_grouped, label='30-Day Moving Average')
ax.set_title("Sales Trend with Moving Average")
ax.set_xlabel("Date")
ax.set_ylabel("Sales Quantity")
ax.legend()
st.pyplot(fig)

# Reorder Points Visualization with GPU acceleration
st.subheader("Reorder Points for Inventory Items")
fig = px.bar(reorder_data, x='Description', y='ReorderPoint', color='ReorderPoint', title="Reorder Points for Inventory Items",
             labels={'Description': "Item Description", 'ReorderPoint': "Reorder Point"}, color_continuous_scale='viridis')
st.plotly_chart(fig)

# Storage Optimization Analysis
st.subheader("Inventory Levels per Store")
storage_analysis = ending_inventory.groupby('Store')['onHand'].sum()
fig, ax = plt.subplots(figsize=(12, 5))
sns.barplot(x=storage_analysis.index, y=storage_analysis.values, palette='coolwarm', ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
ax.set_title("Inventory Levels per Store")
ax.set_xlabel("Store")
ax.set_ylabel("On-Hand Inventory")
st.pyplot(fig)

# Cost Savings Recommendations
st.subheader("Top Vendors by Purchase Amount")
purchase_analysis = purchases.groupby('VendorName')['Dollars'].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(12, 5))
purchase_analysis.head(10).plot(kind='bar', title='Top Vendors by Purchase Amount', ax=ax)
ax.set_xlabel("Vendor Name")
ax.set_ylabel("Total Purchase Cost")
st.pyplot(fig)

st.write("This dashboard provides insights into demand forecasting, inventory optimization, and cost-saving recommendations.")
