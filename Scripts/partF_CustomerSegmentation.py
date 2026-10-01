# ==========================================================
# PART F - CUSTOMER SEGMENTATION
# ==========================================================

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
    print("Connected to PostgreSQL!")

except Exception as e:
    print("Connection failed:")
    print(e)

os.makedirs("figures", exist_ok=True)
os.makedirs("report", exist_ok=True)

# ----------------------------------------------------------
# Load Customer Lifetime Value results
# ----------------------------------------------------------

clv = pd.read_csv(
    "report/clv_results.csv"
)

print(clv.head())

# ----------------------------------------------------------
# Load customer information
# ----------------------------------------------------------

query = """
SELECT
    customer_id,
    city,
    state,
    segment,
    status
FROM customer;
"""

customer = pd.read_sql(query, conn)

print(customer.head())

# ----------------------------------------------------------
# Merge customer information with CLV
# ----------------------------------------------------------

clv = clv.merge(
    customer,
    on="customer_id",
    how="left"
)

print(clv.head())

# ----------------------------------------------------------
# Create CLV customer segments
# ----------------------------------------------------------

clv["Customer_Segment"] = pd.qcut(

    clv["CLV"],

    q=[0, 0.20, 0.50, 0.80, 1.00],

    labels=[
        "Bronze",
        "Silver",
        "Gold",
        "Platinum"
    ]

)

print(
    clv["Customer_Segment"].value_counts()
)

# ----------------------------------------------------------
# Create segment summary table
# ----------------------------------------------------------

segment_summary = clv.groupby("Customer_Segment").agg(

    Customers=("customer_id", "count"),

    Average_CLV=("CLV", "mean"),

    Average_Spending=("Total_Revenue", "mean"),

    Average_Purchase_Frequency=("Transactions", "mean")

).round(2)

print("\nSegment Summary")
print(segment_summary)

# ----------------------------------------------------------
# Customer demographics
# ----------------------------------------------------------

demographics = clv.groupby("Customer_Segment").agg(

    Most_Common_City=("city", lambda x: x.mode().iloc[0]),

    Most_Common_State=("state", lambda x: x.mode().iloc[0]),

    Most_Common_Status=("status", lambda x: x.mode().iloc[0])

)

print("\nCustomer Demographics")
print(demographics)

# ----------------------------------------------------------
# Load product purchasing information
# ----------------------------------------------------------

query = """
SELECT

o.customer_id,

p.category_id,

p.brand

FROM "order" o

JOIN order_item oi
ON o.order_id = oi.order_id

JOIN product p
ON oi.product_id = p.product_id;
"""

products = pd.read_sql(query, conn)

#merged
products = products.merge(

    clv[["customer_id", "Customer_Segment"]],

    on="customer_id",

    how="left"

)

preferences = products.groupby(

    "Customer_Segment"

).agg(

    Favourite_Category=("category_id", lambda x: x.mode().iloc[0]),

    Favourite_Brand=("brand", lambda x: x.mode().iloc[0])

)

print("\nProduct Preferences")
print(preferences)

# ----------------------------------------------------------
# Customer segment distribution
# ----------------------------------------------------------

import matplotlib.pyplot as plt

plt.figure(figsize=(8,6))

clv["Customer_Segment"].value_counts().plot(
    kind="bar"
)

plt.title("Customer Segments Based on CLV")

plt.xlabel("Segment")

plt.ylabel("Number of Customers")

plt.tight_layout()

plt.savefig(
    "figures/clv_customer_segments.png",
    dpi=300
)

plt.close()

segment_summary.to_csv(
    "report/segment_summary.csv"
)

demographics.to_csv(
    "report/customer_demographics.csv"
)

preferences.to_csv(
    "report/product_preferences.csv"
)

clv.to_csv(
    "report/customer_segments.csv",
    index=False
)

print("\n====================================")
print("Part F Completed Successfully")
print("====================================")

print(f"Customers Analysed : {len(clv)}")

print("Customer segmentation table saved.")
print("Segment summary saved.")
print("Demographics summary saved.")
print("Product preferences saved.")
print("Segment chart saved to figures.")

conn.close()

print("Database connection closed.")
