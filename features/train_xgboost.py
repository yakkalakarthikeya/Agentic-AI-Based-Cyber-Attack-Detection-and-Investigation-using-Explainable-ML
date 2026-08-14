import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from xgboost import XGBClassifier


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

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_csv(DATA_FILE)

print("=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

print("Original shape:", df.shape)

print("\nOriginal labels:")
print(df["label"].value_counts())


# ============================================================
# REMOVE DUPLICATE FLOWS
# ============================================================

before = len(df)

df = df.drop_duplicates()

after = len(df)

print("\nDuplicate rows removed:", before - after)
print("Shape after duplicate removal:", df.shape)


# ============================================================
# REMOVE NON-ML COLUMNS
# ============================================================

non_ml_columns = [
    "flow_id",
    "src_ip",
    "dst_ip"
]

existing_columns = [
    col for col in non_ml_columns
    if col in df.columns
]

df = df.drop(
    columns=existing_columns
)


# ============================================================
# SEPARATE FEATURES AND LABEL
# ============================================================

X = df.drop(
    columns=["label"]
)

y = df["label"]


# ============================================================
# CONVERT FEATURES TO NUMERIC
# ============================================================

for column in X.columns:

    X[column] = pd.to_numeric(
        X[column],
        errors="coerce"
    )


# ============================================================
# HANDLE INF / NaN
# ============================================================

X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

missing = X.isnull().sum()

missing = missing[
    missing > 0
].sort_values(
    ascending=False
)

if len(missing) > 0:

    print("\nMissing values before filling:")

    print(missing.to_string())


X = X.fillna(0)


# ============================================================
# REMOVE CONSTANT FEATURES
# ============================================================

constant_columns = [
    column
    for column in X.columns
    if X[column].nunique() <= 1
]

if constant_columns:

    print("\nConstant features removed:")

    for column in constant_columns:
        print("-", column)

    X = X.drop(
        columns=constant_columns
    )


# ============================================================
# ENCODE LABELS
# ============================================================

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)


print("\nClasses:")

for index, label in enumerate(
    label_encoder.classes_
):

    print(
        index,
        "->",
        label
    )


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y_encoded,

    test_size=0.20,

    random_state=42,

    stratify=y_encoded
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# XGBOOST
# ============================================================

model = XGBClassifier(

    objective="multi:softprob",

    num_class=len(
        label_encoder.classes_
    ),

    n_estimators=200,

    max_depth=4,

    learning_rate=0.05,

    subsample=0.7,

    colsample_bytree=0.7,

    min_child_weight=3,

    reg_alpha=0.1,

    reg_lambda=1.0,

    eval_metric="mlogloss",

    random_state=42
)


print("\n" + "=" * 60)
print("TRAINING XGBOOST")
print("=" * 60)


model.fit(
    X_train,
    y_train
)


print("Training completed.")


# ============================================================
# PREDICTION
# ============================================================

y_pred = model.predict(
    X_test
)


# ============================================================
# PROBABILITIES
# ============================================================

probabilities = model.predict_proba(
    X_test
)

confidence = np.max(
    probabilities,
    axis=1
)


# ============================================================
# EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


print("\n" + "=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)

print(
    f"Average confidence: "
    f"{confidence.mean() * 100:.2f}%"
)


print("\nClassification Report:\n")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


print("\nConfusion Matrix:\n")

cm = confusion_matrix(
    y_test,
    y_pred
)

cm_df = pd.DataFrame(
    cm,

    index=label_encoder.classes_,

    columns=label_encoder.classes_
)

print(cm_df)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({

    "feature": X.columns,

    "importance": model.feature_importances_

})


importance = importance.sort_values(

    by="importance",

    ascending=False

)


print("\n" + "=" * 60)
print("XGBOOST FEATURE IMPORTANCE")
print("=" * 60)

print(
    importance.to_string(
        index=False
    )
)


# ============================================================
# SAVE FEATURE IMPORTANCE
# ============================================================

importance_file = os.path.join(

    BASE_DIR,

    "data",

    "xgboost_feature_importance.csv"

)

importance.to_csv(

    importance_file,

    index=False

)


# ============================================================
# SAVE MODEL
# ============================================================

model_file = os.path.join(

    MODEL_DIR,

    "xgboost_model.pkl"

)

encoder_file = os.path.join(

    MODEL_DIR,

    "label_encoder.pkl"

)

feature_file = os.path.join(

    MODEL_DIR,

    "feature_columns.pkl"

)


joblib.dump(
    model,
    model_file
)

joblib.dump(
    label_encoder,
    encoder_file
)

joblib.dump(
    list(X.columns),
    feature_file
)


# ============================================================
# FINAL INFORMATION
# ============================================================

print("\n" + "=" * 60)
print("FILES SAVED")
print("=" * 60)

print(
    model_file
)

print(
    encoder_file
)

print(
    feature_file
)

print(
    importance_file
)

print("\nFinished.")