# ==========================================================
# PART D - CUSTOMER LIFETIME VALUE (CLV) ANALYSIS
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
# Load transaction data for CLV calculation
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

transactions = pd.read_sql(query, conn)

transactions["order_date"] = pd.to_datetime(
    transactions["order_date"]
)

transactions["Revenue"] = (
    transactions["quantity"] *
    transactions["unit_price"]
)
# Revenue is estimated using quantity × available unit price.
# Transactions without matching prices contribute zero revenue.

# ----------------------------------------------------------
# Create customer-level summary table
# ----------------------------------------------------------

customer_summary = transactions.groupby("customer_id").agg(

    Total_Revenue=("Revenue", "sum"),

    Transactions=("order_id", "nunique"),

    Last_Purchase=("order_date", "max")

)

# ----------------------------------------------------------
# Average Purchase Value (APV)
# ----------------------------------------------------------

customer_summary["APV"] = (
    customer_summary["Total_Revenue"] /
    customer_summary["Transactions"]
)

# ----------------------------------------------------------
# Purchase Frequency (PF)
# ----------------------------------------------------------

purchase_frequency = (
    customer_summary["Transactions"].sum() /
    len(customer_summary)
)

print(f"\nPurchase Frequency: {purchase_frequency:.2f}")

# ----------------------------------------------------------
# Churn Rate
# ----------------------------------------------------------

snapshot_date = transactions["order_date"].max()

customer_summary["Days_Since_Last_Purchase"] = (
    snapshot_date -
    customer_summary["Last_Purchase"]
).dt.days



customer_summary["Churned"] = (
    customer_summary["Days_Since_Last_Purchase"] > 90
)

churn_rate = (
    customer_summary["Churned"].sum() /
    len(customer_summary)
)

print(f"Churn Rate: {churn_rate:.4f}")

# ----------------------------------------------------------
# Customer Lifetime Value (CLV)
# ----------------------------------------------------------

customer_summary["CLV"] = (
    customer_summary["APV"] *
    purchase_frequency
) / churn_rate

print("\nCustomer CLV Summary")
print(customer_summary.describe())

# ----------------------------------------------------------
# Top 20 Customers by CLV
# ----------------------------------------------------------

top20 = customer_summary.sort_values(
    by="CLV",
    ascending=False
).head(20)

print("\nTop 20 Customers by CLV")
print(top20)

customer_summary.to_csv(
    "report/clv_results.csv",
    index=True
)

plt.figure(figsize=(10,6))

plt.hist(
    customer_summary["CLV"],
    bins=30
)

plt.title("Customer Lifetime Value Distribution")
plt.xlabel("CLV")
plt.ylabel("Number of Customers")

plt.tight_layout()

plt.savefig(
    "figures/clv_distribution.png",
    dpi=300
)

plt.close()

top20.to_csv(
    "report/top20_clv_customers.csv",
    index=True
)


print("\n====================================")
print("Part D Completed Successfully")
print("====================================")
print(f"Customers Analysed : {len(customer_summary)}")
print("CLV table saved to report/clv_results.csv")
print("Top 20 customers saved to report/top20_clv_customers.csv")
print("CLV distribution chart saved to figures/")

conn.close()

print("Database connection closed.")
