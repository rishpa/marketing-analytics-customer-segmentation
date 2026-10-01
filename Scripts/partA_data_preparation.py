# ==========================================================
# PART A - DATA PREPARATION
# ==========================================================

# Import required libraries
import psycopg2
import pandas as pd

# ----------------------------------------------------------
# Connect to PostgreSQL Database
# ----------------------------------------------------------

conn = psycopg2.connect(
    dbname="marketing_hw2",
    user="rishpa",
    password="Rishpa@123",
    host="localhost",
    port="5432"
)

print("Connected to PostgreSQL!")

# ----------------------------------------------------------
# Load database tables into pandas
# ----------------------------------------------------------

customer = pd.read_sql(
    "SELECT * FROM customer;",
    conn
)

orders = pd.read_sql(
    'SELECT * FROM "order";',
    conn
)

order_item = pd.read_sql(
    "SELECT * FROM order_item;",
    conn
)

product = pd.read_sql(
    "SELECT * FROM product;",
    conn
)

# ----------------------------------------------------------
# Convert date columns
# ----------------------------------------------------------

customer["signup_date"] = pd.to_datetime(
    customer["signup_date"]
)

orders["order_date"] = pd.to_datetime(
    orders["order_date"]
)

# ----------------------------------------------------------
# Display first five rows
# ----------------------------------------------------------

print("\nCustomer Table")
print(customer.head())

print("\nOrder Table")
print(orders.head())

print("\nOrder Item Table")
print(order_item.head())

print("\nProduct Table")
print(product.head())

# ----------------------------------------------------------
# Display dataset information
# ----------------------------------------------------------

print("\n==============================")
print("CUSTOMER INFO")
print("==============================")
customer.info()

print("\n==============================")
print("ORDER INFO")
print("==============================")
orders.info()

print("\n==============================")
print("ORDER ITEM INFO")
print("==============================")
order_item.info()

print("\n==============================")
print("PRODUCT INFO")
print("==============================")
product.info()

# ----------------------------------------------------------
# Summary statistics
# ----------------------------------------------------------

print("\n==============================")
print("SUMMARY STATISTICS")
print("==============================")

print("\nCustomer")
print(customer.describe(include="all"))

print("\nOrders")
print(orders.describe(include="all"))

print("\nOrder Items")
print(order_item.describe(include="all"))

print("\nProduct")
print(product.describe(include="all"))

# ----------------------------------------------------------
# Missing values
# ----------------------------------------------------------

print("\n==============================")
print("MISSING VALUES")
print("==============================")

print("\nCustomer")
print(customer.isnull().sum())

print("\nOrders")
print(orders.isnull().sum())

print("\nOrder Items")
print(order_item.isnull().sum())

print("\nProduct")
print(product.isnull().sum())

# ----------------------------------------------------------
# Close database connection
# ----------------------------------------------------------

conn.close()

print("\nDatabase connection closed.")