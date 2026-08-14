import os

# Limit numerical-library memory/thread usage
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "combined_cyber_attacks.csv"
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "models",
    "xgboost_model.pkl"
)

ENCODER_FILE = os.path.join(
    BASE_DIR,
    "models",
    "label_encoder.pkl"
)

FEATURE_FILE = os.path.join(
    BASE_DIR,
    "models",
    "feature_columns.pkl"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "xai_results"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("LOADING DATASET")
print("=" * 60)

df = pd.read_csv(DATA_FILE)

print("Dataset shape:", df.shape)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading XGBoost model...")

model = joblib.load(
    MODEL_FILE
)

label_encoder = joblib.load(
    ENCODER_FILE
)

feature_columns = joblib.load(
    FEATURE_FILE
)

print("Model loaded successfully.")

print("\nClasses:")

for i, label in enumerate(
    label_encoder.classes_
):
    print(
        i,
        "->",
        label
    )


# ============================================================
# PREPARE FEATURES
# ============================================================

drop_columns = [
    "flow_id",
    "src_ip",
    "dst_ip",
    "label"
]

existing_columns = [
    c for c in drop_columns
    if c in df.columns
]

X = df.drop(
    columns=existing_columns
)


# Make exactly the same
# feature order as training

X = X.reindex(
    columns=feature_columns,
    fill_value=0
)


# Convert to numeric

for column in X.columns:

    X[column] = pd.to_numeric(
        X[column],
        errors="coerce"
    )


# Handle invalid values

X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

X = X.fillna(0)


# ============================================================
# TAKE SMALL SAMPLE
# ============================================================

SAMPLE_SIZE = min(
    500,
    len(X)
)

X_sample = X.sample(
    n=SAMPLE_SIZE,
    random_state=42
)

print(
    "\nXAI sample size:",
    len(X_sample)
)


# ============================================================
# XGBOOST NATIVE FEATURE CONTRIBUTIONS
# ============================================================

print("\nCalculating feature contributions...")

booster = model.get_booster()

# XGBoost native contribution calculation
# Last column = bias/base value

contributions = booster.predict(
    __import__("xgboost").DMatrix(X_sample),
    pred_contribs=True
)


print(
    "Contribution array shape:",
    contributions.shape
)


# ============================================================
# HANDLE MULTI-CLASS OUTPUT
# ============================================================

# For multiclass XGBoost, pred_contribs can have:
#
# samples × classes × (features + 1)
#
# or an equivalent flattened representation
# depending on XGBoost version.

num_classes = len(
    label_encoder.classes_
)

num_features = len(
    feature_columns
)


if contributions.ndim == 3:

    # Expected:
    # samples × classes × (features + 1)

    feature_contributions = contributions[
        :, :, :-1
    ]

else:

    # Flattened multiclass format

    feature_contributions = contributions.reshape(
        SAMPLE_SIZE,
        num_classes,
        num_features + 1
    )[:, :, :-1]


# ============================================================
# GLOBAL FEATURE IMPORTANCE
# ============================================================

# Absolute contribution across:
#
# samples
# classes
#
# This tells us which features
# have the largest overall impact.

global_values = np.mean(
    np.abs(
        feature_contributions
    ),
    axis=(0, 1)
)


global_importance = pd.DataFrame({

    "feature": feature_columns,

    "mean_abs_contribution": global_values

})


global_importance = global_importance.sort_values(
    by="mean_abs_contribution",
    ascending=False
)


# ============================================================
# DISPLAY GLOBAL IMPORTANCE
# ============================================================

print("\n" + "=" * 60)
print("GLOBAL XAI FEATURE IMPORTANCE")
print("=" * 60)

print(
    global_importance.head(20).to_string(
        index=False
    )
)


# ============================================================
# SAVE GLOBAL IMPORTANCE
# ============================================================

global_file = os.path.join(
    OUTPUT_DIR,
    "global_feature_contributions.csv"
)

global_importance.to_csv(
    global_file,
    index=False
)

print(
    "\nSaved:",
    global_file
)


# ============================================================
# CLASS-WISE FEATURE IMPORTANCE
# ============================================================

print("\n" + "=" * 60)
print("CLASS-WISE FEATURE IMPORTANCE")
print("=" * 60)


for class_index, class_name in enumerate(
    label_encoder.classes_
):

    class_values = feature_contributions[
        :,
        class_index,
        :
    ]

    class_importance = np.mean(
        np.abs(class_values),
        axis=0
    )

    class_df = pd.DataFrame({

        "feature": feature_columns,

        "mean_abs_contribution": class_importance

    })

    class_df = class_df.sort_values(
        by="mean_abs_contribution",
        ascending=False
    )

    print(
        f"\n{class_name}"
    )

    print(
        class_df.head(10).to_string(
            index=False
        )
    )

    class_file = os.path.join(
        OUTPUT_DIR,
        f"{class_name}_feature_contributions.csv"
    )

    class_df.to_csv(
        class_file,
        index=False
    )


# ============================================================
# BAR CHART
# ============================================================

print("\nCreating XAI feature importance plot...")

top_features = global_importance.head(10).sort_values(
    "mean_abs_contribution"
)

fig, ax = plt.subplots(
    figsize=(7, 5),
    dpi=100
)

ax.barh(
    top_features["feature"],
    top_features["mean_abs_contribution"]
)

ax.set_xlabel(
    "Mean absolute feature contribution"
)

ax.set_ylabel(
    "Feature"
)

ax.set_title(
    "XAI Feature Importance"
)

fig.tight_layout()

plot_file = os.path.join(
    OUTPUT_DIR,
    "global_feature_importance.png"
)

fig.savefig(
    plot_file,
    dpi=100
)

plt.close(fig)

print(
    "Saved:",
    plot_file
)
# ============================================================
# FINISHED
# ============================================================

print("\n" + "=" * 60)
print("XAI ANALYSIS COMPLETED")
print("=" * 60)

print(
    "\nResults saved in:"
)

print(
    OUTPUT_DIR
)

print("\nFiles generated:")

print(
    "global_feature_contributions.csv"
)

print(
    "global_feature_importance.png"
)

for class_name in label_encoder.classes_:

    print(
        f"{class_name}_feature_contributions.csv"
    )

print(
    "\nNo SHAP/Numba/llvmlite import was required."
)