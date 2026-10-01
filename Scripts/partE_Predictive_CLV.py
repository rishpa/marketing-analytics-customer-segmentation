# ==========================================================
# PART E - PREDICTIVE CUSTOMER LIFETIME VALUE (CLV)
# ==========================================================

import psycopg2
import pandas as pd
import os

from lifetimes.utils import calibration_and_holdout_data
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)


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
# Load transaction data from PostgreSQL
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

# ----------------------------------------------------------
# Calculate transaction revenue
# ----------------------------------------------------------
#
# Revenue is calculated as quantity × unit price.
# Transactions without matching price information have missing revenue values.

transactions["Revenue"] = (
    transactions["quantity"] *
    transactions["unit_price"]
)

# ----------------------------------------------------------
# Create calibration and holdout datasets
# ----------------------------------------------------------

holdout = calibration_and_holdout_data(
    transactions,
    customer_id_col="customer_id",
    datetime_col="order_date",
    monetary_value_col="Revenue",
    calibration_period_end="2025-08-31",
    observation_period_end="2026-02-21"
)

print(f"Customers in holdout dataset: {len(holdout)}")

# ----------------------------------------------------------
# Train BG/NBD model
# ----------------------------------------------------------

bgf = BetaGeoFitter(penalizer_coef=0.01)

bgf.fit(
    holdout["frequency_cal"],
    holdout["recency_cal"],
    holdout["T_cal"]
)

print("\nBG/NBD model trained successfully.")

# ----------------------------------------------------------
# Predict purchases during holdout period
# ----------------------------------------------------------

holdout["Predicted_Purchases"] = bgf.predict(
    holdout["duration_holdout"],
    holdout["frequency_cal"],
    holdout["recency_cal"],
    holdout["T_cal"]
)

# ----------------------------------------------------------
# Evaluate BG/NBD model performance
# ----------------------------------------------------------

# Compare predicted purchases with actual purchases
# observed during the holdout period.

actual = holdout["frequency_holdout"]
predicted = holdout["Predicted_Purchases"]

rmse = mean_squared_error(
    actual,
    predicted
) ** 0.5

mae = mean_absolute_error(
    actual,
    predicted
)

r2 = r2_score(
    actual,
    predicted
)

print("\n====================================")
print("Model Evaluation")
print("====================================")
print(f"RMSE : {rmse:.3f}")
print(f"MAE  : {mae:.3f}")
print(f"R²   : {r2:.3f}")

# ----------------------------------------------------------
# Prepare data for Gamma-Gamma model
# ----------------------------------------------------------

gg_data = holdout[
    (holdout["frequency_cal"] > 0) &
    (holdout["monetary_value_cal"] > 0)
].copy()

print(f"\nCustomers used for Gamma-Gamma: {len(gg_data)}")

# ----------------------------------------------------------
# Train Gamma-Gamma model
# ----------------------------------------------------------

ggf = GammaGammaFitter(
    penalizer_coef=0.01
)

ggf.fit(
    gg_data["frequency_cal"],
    gg_data["monetary_value_cal"]
)

print("Gamma-Gamma model trained successfully.")

# ----------------------------------------------------------
# Predict monetary value
# ----------------------------------------------------------

gg_data["Predicted_Monetary"] = (
    ggf.conditional_expected_average_profit(
        gg_data["frequency_cal"],
        gg_data["monetary_value_cal"]
    )
)

print("\nPredicted Monetary Values")
print(
    gg_data[
        [
            "monetary_value_cal",
            "Predicted_Monetary"
        ]
    ].head()
)

# ----------------------------------------------------------
# Predict Customer Lifetime Value
# ----------------------------------------------------------

gg_data["Predicted_CLV"] = (
    gg_data["Predicted_Purchases"] *
    gg_data["Predicted_Monetary"]
)
print("\nTop Predicted CLV Customers")

top20 = gg_data.sort_values(
    by="Predicted_CLV",
    ascending=False
).head(20)

print(top20)

# ----------------------------------------------------------
# Save prediction results
# ----------------------------------------------------------

# Save prediction results for reporting

gg_data.to_csv(
    "report/predictive_clv_results.csv",
    index=True
)

top20.to_csv(
    "report/top20_predictive_clv.csv",
    index=True
)

# ----------------------------------------------------------
# Prediction summary statistics
# ----------------------------------------------------------

print("\nPrediction Summary")
print(
    gg_data[
        ["Predicted_Purchases", "Predicted_Monetary", "Predicted_CLV"]
    ].describe()
)

print("\n====================================")
print("Part E Completed Successfully")
print("====================================")
print(f"Customers Analysed : {len(gg_data)}")
print(f"RMSE : {rmse:.3f}")
print(f"MAE  : {mae:.3f}")
print(f"R²   : {r2:.3f}")
print("Predictive CLV saved to report/predictive_clv_results.csv")
print("Top 20 predictive CLV customers saved to report/top20_predictive_clv.csv")

conn.close()

print("Database connection closed.")

