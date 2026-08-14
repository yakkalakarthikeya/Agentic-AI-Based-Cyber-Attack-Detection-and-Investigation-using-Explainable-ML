import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "combined_cyber_dataset.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "ml_ready_dataset.csv"
)

df = pd.read_csv(INPUT_FILE)

print("Original shape:", df.shape)

print("\nOriginal labels:")
print(df["label"].value_counts())

# Columns that should not be used by ML
remove_columns = [
    "flow_id",
    "src_ip",
    "dst_ip",
    "source_dataset"
]

remove_columns = [
    col for col in remove_columns
    if col in df.columns
]

df = df.drop(columns=remove_columns)

# Remove columns that are completely empty
empty_columns = [
    col for col in df.columns
    if col != "label" and df[col].isna().all()
]

print("\nCompletely empty columns:")
print(empty_columns)

df = df.drop(columns=empty_columns)

# Convert feature columns to numeric
feature_columns = [
    col for col in df.columns
    if col != "label"
]

for col in feature_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# Display remaining missing values
print("\nMissing values:")
print(
    df.isna()
    .sum()
    .sort_values(ascending=False)
    .to_string()
)

# Save the cleaned master dataset
df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n================================")
print("ML DATASET PREPARATION COMPLETE")
print("================================")

print("Shape:", df.shape)
print("Output:", OUTPUT_FILE)

print("\nLabels:")
print(df["label"].value_counts())

print("\nFeatures:")
print(
    [col for col in df.columns if col != "label"]
)