import os
import joblib
import pandas as pd


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

ENCODER_FILE = os.path.join(
    BASE_DIR,
    "models",
    "label_encoder.pkl"
)


def explain_prediction(data):

    model = joblib.load(MODEL_FILE)
    feature_columns = joblib.load(FEATURE_FILE)
    label_encoder = joblib.load(ENCODER_FILE)

    row = {}

    for feature in feature_columns:

        value = data.get(feature, 0)

        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0

        row[feature] = value

    df = pd.DataFrame(
        [row],
        columns=feature_columns
    )

    prediction_encoded = model.predict(df)[0]

    probabilities = model.predict_proba(df)[0]

    prediction = label_encoder.inverse_transform(
        [int(prediction_encoded)]
    )[0]

    probability_dict = {}

    for class_id, probability in zip(
        model.classes_,
        probabilities
    ):

        class_name = label_encoder.inverse_transform(
            [int(class_id)]
        )[0]

        probability_dict[str(class_name)] = round(
            float(probability) * 100,
            2
        )

    feature_importances = model.feature_importances_

    explanations = []

    for feature, importance, value in zip(
        feature_columns,
        feature_importances,
        df.iloc[0].values
    ):

        explanations.append({
            "feature": feature,
            "importance": round(
                float(importance),
                6
            ),
            "value": float(value)
        })

    explanations.sort(
        key=lambda x: abs(x["importance"]),
        reverse=True
    )

    return {
        "prediction": str(prediction),
        "confidence": round(
            probability_dict[str(prediction)],
            2
        ),
        "probabilities": probability_dict,
        "top_features": explanations[:10]
    }