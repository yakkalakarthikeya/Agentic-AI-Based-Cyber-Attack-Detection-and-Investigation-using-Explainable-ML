import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "models",
    "xgboost_model.pkl"
)

FEATURE_FILE = os.path.join(
    BASE_DIR,
    "models",
    "feature_columns.pkl"
)


model = joblib.load(
    MODEL_FILE
)

feature_columns = joblib.load(
    FEATURE_FILE
)


def get_xai_evidence(flow, top_n=10):

    data = {}

    for feature in feature_columns:

        value = flow.get(
            feature,
            0
        )

        try:

            value = float(value)

            if not np.isfinite(value):
                value = 0

        except:

            value = 0

        data[feature] = value

    X = pd.DataFrame(
        [data],
        columns=feature_columns
    )

    booster = model.get_booster()

    dmatrix = xgb.DMatrix(X)

    contributions = booster.predict(
        dmatrix,
        pred_contribs=True
    )

    num_classes = len(
        model.classes_
    )

    num_features = len(
        feature_columns
    )

    if contributions.ndim == 3:

        values = contributions[
            0,
            :,
            :-1
        ]

        importance = np.mean(
            np.abs(values),
            axis=0
        )

    else:

        values = contributions.reshape(
            1,
            num_classes,
            num_features + 1
        )[0, :, :-1]

        importance = np.mean(
            np.abs(values),
            axis=0
        )

    result = pd.DataFrame({

        "feature": feature_columns,

        "importance": importance

    })

    result = result.sort_values(
        "importance",
        ascending=False
    )

    result = result.head(
        top_n
    )

    evidence = []

    for _, row in result.iterrows():

        evidence.append({

            "feature": row["feature"],

            "importance": round(
                float(row["importance"]),
                6
            ),

            "value": float(
                X.iloc[0][row["feature"]]
            )

        })

    return evidence