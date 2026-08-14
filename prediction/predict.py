import os
import sys
import joblib
import numpy as np
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


model = joblib.load(MODEL_FILE)
label_encoder = joblib.load(ENCODER_FILE)
feature_columns = joblib.load(FEATURE_FILE)


KNOWN_ATTACKS = {
    "BRUTE_FORCE",
    "PORT_SCAN",
    "HTTP_FLOOD",
    "DNS_TUNNELING"
}


BENIGN_LABELS = {
    "BENIGN",
    "NORMAL"
}


CONFIDENCE_THRESHOLD = 70.0
MARGIN_THRESHOLD = 20.0


def predict_attack(flow_data):

    input_data = {}

    for feature in feature_columns:

        value = flow_data.get(feature, 0)

        try:
            value = float(value)
        except (ValueError, TypeError):
            value = 0.0

        input_data[feature] = value

    df = pd.DataFrame(
        [input_data],
        columns=feature_columns
    )

    probabilities = model.predict_proba(df)[0]

    predicted_index = int(
        np.argmax(probabilities)
    )

    predicted_label = label_encoder.inverse_transform(
        [predicted_index]
    )[0]

    sorted_probabilities = np.sort(
        probabilities
    )[::-1]

    confidence = float(
        probabilities[predicted_index] * 100
    )

    if len(sorted_probabilities) > 1:

        second_probability = float(
            sorted_probabilities[1] * 100
        )

    else:

        second_probability = 0.0

    probability_margin = (
        confidence - second_probability
    )

    probability_dict = {}

    for label, probability in zip(
        label_encoder.classes_,
        probabilities
    ):

        probability_dict[str(label)] = round(
            float(probability * 100),
            2
        )

    if predicted_label in BENIGN_LABELS:

        result = "NORMAL"

        attack_type = "BENIGN"

        classification_status = "KNOWN"

    elif (
        predicted_label in KNOWN_ATTACKS
        and confidence >= CONFIDENCE_THRESHOLD
        and probability_margin >= MARGIN_THRESHOLD
    ):

        result = "ATTACK"

        attack_type = str(
            predicted_label
        )

        classification_status = "KNOWN"

    else:

        result = "ATTACK"

        attack_type = "UNKNOWN_ATTACK"

        classification_status = "POSSIBLE_UNSEEN_ATTACK"

    return {

        "result": result,

        "prediction": str(
            predicted_label
        ),

        "attack_type": attack_type,

        "classification_status":
            classification_status,

        "confidence": round(
            confidence,
            2
        ),

        "second_highest_confidence":
            round(
                second_probability,
                2
            ),

        "probability_margin":
            round(
                probability_margin,
                2
            ),

        "probabilities":
            probability_dict,

        "llm_required":
            classification_status ==
            "POSSIBLE_UNSEEN_ATTACK"
    }


if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("CYBER ATTACK PREDICTION ENGINE")
    print("=" * 70)

    print("\nLoaded model classes:")

    print(
        list(
            label_encoder.classes_
        )
    )

    print("\nFeature count:")

    print(
        len(feature_columns)
    )

    print("\nPrediction engine ready.")