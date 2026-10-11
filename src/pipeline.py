
from pathlib import Path

import numpy as np
import pandas as pd

# Reproducible simulated data
rng = np.random.default_rng(42)

# Resolve paths from the project root
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 1. GENERATE RAW TRANSACTION DATA
# --------------------------------------------------

n = 10_000

transaction_types = [
    "deposit", "withdrawal", "payment",
    "transfer", "trading"
]

data = pd.DataFrame({
    "transaction_id": range(1, n + 1),
    "customer_id": rng.integers(1001, 2501, n),
    "transaction_date": (
        pd.Timestamp("2026-01-01")
        + pd.to_timedelta(
            rng.integers(0, 181, n), unit="D"
        )
    ),
    "transaction_type": rng.choice(
        transaction_types, n
    ),
    "amount": np.round(
        rng.lognormal(7, 1, n), 2
    ),
    "status": rng.choice(
        ["success", "failed", "pending"],
        n,
        p=[0.94, 0.04, 0.02]
    ),
    "channel": rng.choice(
        ["mobile", "web", "api"],
        n,
        p=[0.65, 0.25, 0.10]
    )
})

# Introduce realistic data-quality problems
missing_amount_rows = rng.choice(
    data.index, size=25, replace=False
)
data.loc[missing_amount_rows, "amount"] = np.nan

missing_channel_rows = rng.choice(
    data.index, size=20, replace=False
)
data.loc[missing_channel_rows, "channel"] = None

# Add duplicate records
duplicates = data.sample(
    n=15, random_state=42
)
data = pd.concat(
    [data, duplicates], ignore_index=True
)

raw_path = RAW_DIR / "transactions.csv"
data.to_csv(raw_path, index=False)

print("Raw data created:", data.shape)

# --------------------------------------------------
# 2. CLEAN AND VALIDATE THE DATA
# --------------------------------------------------

clean = pd.read_csv(
    raw_path,
    parse_dates=["transaction_date"]
)

rows_before = len(clean)

# Remove duplicate transaction IDs
clean = clean.drop_duplicates(
    subset=["transaction_id"],
    keep="first"
)

# Remove rows with missing critical fields
clean = clean.dropna(
    subset=[
        "transaction_id",
        "customer_id",
        "transaction_date",
        "transaction_type",
        "amount",
        "status"
    ]
)

# Handle missing channel values
clean["channel"] = clean["channel"].fillna("unknown")

# Validate transaction amounts
clean = clean[clean["amount"] >= 0]

# Standardize text columns
for column in [
    "transaction_type", "status", "channel"
]:
    clean[column] = (
        clean[column].astype(str).str.strip().str.lower()
    )

# Save the processed dataset
clean_path = PROCESSED_DIR / "transactions_clean.csv"
clean.to_csv(clean_path, index=False)

# --------------------------------------------------
# 3. PRINT DATA-QUALITY REPORT
# --------------------------------------------------

print("\n--- DATA QUALITY REPORT ---")
print("Rows before cleaning:", rows_before)
print("Rows after cleaning:", len(clean))
print("Rows removed:", rows_before - len(clean))
print(
    "Duplicate transaction IDs:",
    clean["transaction_id"].duplicated().sum()
)
print(
    "Missing values remaining:",
    clean.isnull().sum().sum()
)

# --------------------------------------------------
# 4. GENERATE A BASIC BUSINESS SUMMARY
# --------------------------------------------------

successful = clean[clean["status"] == "success"]

print("\n--- BUSINESS SUMMARY ---")
print("Total transactions:", len(clean))
print("Successful transactions:", len(successful))
print(
    "Success rate (%):",
    round(len(successful) / len(clean) * 100, 2)
)
print(
    "Total value of successful transactions:",
    round(successful["amount"].sum(), 2)
)
print(
    "Average transaction amount:",
    round(clean["amount"].mean(), 2)
)

print("\nClean dataset saved to:", clean_path)
