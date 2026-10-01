# ==========================================================
# PART B - EXPLORATORY DATA ANALYSIS (EDA)
# ==========================================================

# Import required libraries
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import os

# ----------------------------------------------------------
# Connect to PostgreSQL Database
# ----------------------------------------------------------

try:
    conn = psycopg2.connect(
        dbname="marketing_hw2",
        user="rishpa",
        password="Rishpa@123",
        host="localhost",
        port="5432"
    )

    print("Successfully connected to the database!")

except Exception as e:
    print("Connection failed:")
    print(e)

# ----------------------------------------------------------
# Create figures folder
# ----------------------------------------------------------

os.makedirs("figures", exist_ok=True)

# ----------------------------------------------------------
# Load integrated dataset
# ----------------------------------------------------------

query = """
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    c.city,
    c.state,
    c.segment,
    c.status,
    oi.product_id,
    oi.quantity,
    oi.item_discount,
    p.category_id,
    p.brand,
    p.sku_name
FROM "order" o

JOIN customer c
ON o.customer_id = c.customer_id

JOIN order_item oi
ON o.order_id = oi.order_id

JOIN product p
ON oi.product_id = p.product_id;
"""

df = pd.read_sql(query, conn)

df["order_date"] = pd.to_datetime(
    df["order_date"]
)

# ----------------------------------------------------------
# Figure 1 - Purchase Frequency Distribution
# ----------------------------------------------------------

purchase_freq = (
    df.groupby("customer_id")["order_id"]
      .nunique()
      .reset_index(name="orders")
)

plt.figure(figsize=(10,6))

plt.hist(
    purchase_freq["orders"],
    bins=30
)

plt.title("Purchase Frequency Distribution")
plt.xlabel("Number of Orders")
plt.ylabel("Number of Customers")

plt.tight_layout()

plt.savefig(
    "figures/purchase_frequency.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# Figure 2 - Customer Segment Distribution
# ----------------------------------------------------------

segment_counts = (
    df[["customer_id", "segment"]]
    .drop_duplicates()
    .groupby("segment")
    .size()
)

plt.figure(figsize=(8,5))

segment_counts.plot(
    kind="bar",
    ax=plt.gca()
)

plt.title("Customer Segment Distribution")
plt.xlabel("Segment")
plt.ylabel("Customers")

plt.tight_layout()

plt.savefig(
    "figures/customer_segments.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# Figure 3 - Customer Status
# ----------------------------------------------------------

status_counts = (
    df[["customer_id", "status"]]
    .drop_duplicates()
    .groupby("status")
    .size()
)

plt.figure(figsize=(6,6))

plt.pie(
    status_counts,
    labels=status_counts.index,
    autopct="%1.1f%%"
)

plt.title("Customer Status")

plt.savefig(
    "figures/customer_status.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# Figure 4 - Monthly Orders
# ----------------------------------------------------------

monthly_orders = (
    df.groupby(df["order_date"].dt.to_period("M"))
      .order_id.nunique()
)

monthly_orders.index = monthly_orders.index.astype(str)

plt.figure(figsize=(14,6))

monthly_orders.plot(
    ax=plt.gca()
)

plt.title("Monthly Orders")
plt.xlabel("Month")
plt.ylabel("Orders")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    "figures/monthly_orders.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# Figure 5 - Product Categories
# ----------------------------------------------------------

top_categories = (
    df.groupby("category_id")["quantity"]
      .sum()
      .sort_values(ascending=False)
)

plt.figure(figsize=(10,6))

top_categories.plot(
    kind="bar",
    ax=plt.gca()
)

plt.title("Products Sold by Category")
plt.xlabel("Category")
plt.ylabel("Quantity Sold")

plt.tight_layout()

plt.savefig(
    "figures/category_sales.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# Figure 6 - Top Brands
# ----------------------------------------------------------

top_brands = (
    df.groupby("brand")["quantity"]
      .sum()
      .sort_values(ascending=False)
      .head(15)
)

plt.figure(figsize=(12,6))

top_brands.plot(
    kind="bar",
    ax=plt.gca()
)

plt.title("Top 15 Brands by Quantity Sold")
plt.xlabel("Brand")
plt.ylabel("Quantity")

plt.tight_layout()

plt.savefig(
    "figures/top_brands.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# Close database connection
# ----------------------------------------------------------

conn.close()

print("\n====================================")
print("Part B Completed Successfully")
print("====================================")
print("EDA figures saved to figures/")
print("Database connection closed.")