import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "combined_cyber_attacks.csv"
)

datasets = {
    "BENIGN": "normal_flow.csv",
    "PORT_SCAN": "port_scan_04_flows.csv",
    "BRUTE_FORCE": "bruteforce_01_flows.csv",
    "HTTP_FLOOD": "http_flood_01_flows.csv",
    "DNS_TUNNELING": "dns_tunneling_01_flows.csv"
}

all_data = []

for label, filename in datasets.items():

    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        print(f"File not found: {filename}")
        continue

    df = pd.read_csv(filepath)

    if "label" in df.columns:
        df = df.drop(columns=["label"])

    df["label"] = label

    all_data.append(df)

    print(f"{label} -> {len(df)} rows")

if not all_data:
    raise SystemExit("No CSV files found.")

combined = pd.concat(
    all_data,
    ignore_index=True,
    sort=False
)

combined.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("DATASETS COMBINED SUCCESSFULLY")
print("===================================")

print("Total rows:", len(combined))
print("Total columns:", len(combined.columns))

print("\nLabels:")
print(combined["label"].value_counts())

print("\nSaved to:")
print(OUTPUT_FILE)