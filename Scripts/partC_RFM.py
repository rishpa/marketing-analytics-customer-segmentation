# ==========================================================
# PART C - RFM ANALYSIS & CUSTOMER SEGMENTATION
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
    print("Connected to PostgreSQL!")

except Exception as e:
    print(e)

os.makedirs("figures", exist_ok=True)
os.makedirs("report", exist_ok=True)

# ----------------------------------------------------------
# Load order data with available prices
# ----------------------------------------------------------

query = """
SELECT
    o.customer_id,
    o.order_id,
    o.order_date,
    oi.quantity,
    pc.unit_price
FROM "order" o

JOIN order_item oi
ON o.order_id = oi.order_id

LEFT JOIN price_change pc
ON oi.product_id = pc.product_id
AND o.year = pc.year
AND o.week = pc.week;
"""

orders = pd.read_sql(query, conn)

# ----------------------------------------------------------
# Convert dates into datetime format
# ----------------------------------------------------------

orders["order_date"] = pd.to_datetime(orders["order_date"])

snapshot_date = orders["order_date"].max() + pd.Timedelta(days=1)

# ----------------------------------------------------------
# Calculate monetary value for each purchased item
# ----------------------------------------------------------

# Monetary value is calculated only where price information 
# is available. Missing prices remain NaN and therefore 
# contribute zero to the customer's total monetary value.

orders["Sales"] = (
    orders["quantity"] *
    orders["unit_price"]
)




# ----------------------------------------------------------
# Calculate RFM Metrics
# ----------------------------------------------------------

rfm = orders.groupby("customer_id").agg({

    "order_date": lambda x: (snapshot_date - x.max()).days,

    "order_id": "nunique",

    "Sales": "sum"

})

rfm.columns = ["Recency", "Frequency", "Monetary"]

print("\nRFM Summary")
print(rfm.describe())

# ----------------------------------------------------------
# Calculate RFM Scores (1–5)
# ----------------------------------------------------------

rfm["R_Score"] = pd.qcut(
    rfm["Recency"],
    5,
    labels=[5,4,3,2,1]
)

rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    5,
    labels=[1,2,3,4,5]
)

rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    5,
    labels=[1,2,3,4,5]
)

# ----------------------------------------------------------
# Create a three-digit RFM score for customer segmentation
# ----------------------------------------------------------

rfm["RFM_Score"] = (
    rfm["R_Score"].astype(str) +
    rfm["F_Score"].astype(str) +
    rfm["M_Score"].astype(str)
)


# ----------------------------------------------------------
# Distribution of RFM Scores
# ----------------------------------------------------------

plt.figure(figsize=(12,6))

rfm["RFM_Score"].value_counts().sort_index().plot(
    kind="bar",
    ax=plt.gca()
)

plt.title("Distribution of RFM Scores")
plt.xlabel("RFM Score")
plt.ylabel("Number of Customers")

plt.tight_layout()

plt.savefig(
    "figures/rfm_distribution.png",
    dpi=300
)

plt.close()


# ----------------------------------------------------------
# Customer Segmentation
# ----------------------------------------------------------

def segment_customer(row):

    r = int(row["R_Score"])
    f = int(row["F_Score"])

    if r >= 4 and f >= 4:
        return "Champions"

    elif r >= 3 and f >= 4:
        return "Loyal Customers"

    elif r >= 4 and f >= 2:
        return "Potential Loyalists"

    elif r <= 2 and f >= 4:
        return "At Risk"

    elif r <= 2 and f <= 2:
        return "Lost Customers"

    else:
        return "Needs Attention"


# Assign segment to each customer
rfm["Segment"] = rfm.apply(segment_customer, axis=1)

# ----------------------------------------------------------
# Display customer segments
# ----------------------------------------------------------

segment_counts = rfm["Segment"].value_counts()

print("\nCustomer Segments")
print(segment_counts)

# ----------------------------------------------------------
# Save RFM results
# ----------------------------------------------------------

os.makedirs("report", exist_ok=True)

rfm.to_csv(
    "report/rfm_results.csv",
    index=True
)

# ----------------------------------------------------------
# Create customer segment chart
# ----------------------------------------------------------

plt.figure(figsize=(10,6))

segment_counts.plot(
    kind="bar",
    ax=plt.gca()
)

plt.title("Customer Segments")
plt.xlabel("Segment")
plt.ylabel("Number of Customers")

plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    "figures/customer_segments_rfm.png",
    dpi=300
)

plt.close()

print("\nTop 10 Customers")

top10 = rfm.sort_values(
    by=["RFM_Score", "Frequency", "Monetary"],
    ascending=False
).head(10)

print(top10)

print("\n====================================")
print("Part C Completed Successfully")
print("====================================")
print(f"Customers Analysed : {len(rfm)}")
print("RFM results saved to report/rfm_results.csv")
print("RFM distribution chart saved to figures/")
print("Customer segmentation chart saved to figures/")

# ----------------------------------------------------------
# Close database connection
# ----------------------------------------------------------

conn.close()

print("Database connection closed.")

