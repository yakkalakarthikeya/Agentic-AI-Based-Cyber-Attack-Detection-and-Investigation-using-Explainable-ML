from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import traceback

from prediction.predict import predict_attack
from xai.live_explainer import explain_prediction
from agent.investigation_agent import CyberInvestigationAgent


app = Flask(__name__)

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://127.0.0.1:5002",
                "http://localhost:5002"
            ]
        }
    }
)


agent = CyberInvestigationAgent()


@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "running",
        "message": "Cyber Attack Investigation API",
        "endpoints": [
            "/health",
            "/analyze"
        ]
    })


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy"
    })


@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "No input data provided"
            }), 400


        print("\n")
        print("=" * 70)
        print("CYBER ATTACK INVESTIGATION")
        print("=" * 70)


        # =========================================
        # 1. ML PREDICTION
        # =========================================

        prediction_result = predict_attack(data)

        print("\nML PREDICTION:")
        print(
            json.dumps(
                prediction_result,
                indent=4
            )
        )


        # =========================================
        # 2. XAI
        # =========================================

        xai_result = explain_prediction(data)

        print("\nXAI EVIDENCE:")

        print(
            json.dumps(
                xai_result,
                indent=4
            )
        )


        # =========================================
        # 3. INVESTIGATION DATA
        # =========================================

        investigation_data = {

            "ml_prediction":
                prediction_result,

            "xai_evidence":
                xai_result,

            "network_flow":
                data
        }


        # =========================================
        # 4. GROQ INVESTIGATION
        # =========================================

        investigation_report = agent.investigate(
            investigation_data
        )


        print("\nLLM INVESTIGATION REPORT:")

        print(
            investigation_report
        )


        # =========================================
        # 5. FINAL RESPONSE
        # =========================================

        return jsonify({

            "success": True,

            "ml_prediction":
                prediction_result,

            "xai_evidence":
                xai_result,

            "investigation_report":
                investigation_report
        })


    except Exception as e:

        print("\nERROR:")

        traceback.print_exc()

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )