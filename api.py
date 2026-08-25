from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import traceback

from prediction.predict import predict_attack
from xai.live_explainer import explain_prediction
from agent.investigation_agent import CyberInvestigationAgent


app = Flask(__name__)


# ==========================================================
# CORS CONFIGURATION
# ==========================================================

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


# ==========================================================
# AGENT INITIALIZATION
# ==========================================================

agent = CyberInvestigationAgent()


# ==========================================================
# HOME
# ==========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "status": "running",

        "message":
            "Agentic Cyber Attack Investigation API",

        "architecture": [

            "Network Flow Input",

            "XGBoost Attack Detection",

            "SHAP Explainable AI",

            "Autonomous Agent Decision",

            "MITRE ATT&CK Knowledge Retrieval",

            "Evidence Evaluation",

            "AI Investigation Report"

        ],

        "endpoints": [

            "/health",

            "/analyze"

        ]

    })


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({

        "status": "healthy",

        "agent": "active",

        "architecture":
            "Agentic Cyber Attack Investigation"

    })


# ==========================================================
# MAIN ANALYSIS ENDPOINT
# ==========================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        # ==================================================
        # 0. RECEIVE NETWORK FLOW
        # ==================================================

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "error":
                    "No input data provided"

            }), 400


        print("\n")
        print("=" * 70)
        print("AGENTIC CYBER ATTACK INVESTIGATION")
        print("=" * 70)


        # ==================================================
        # 1. XGBOOST ML PREDICTION
        # ==================================================

        print("\n[1] RUNNING XGBOOST ATTACK DETECTION...")

        prediction_result = predict_attack(data)

        print("\nML PREDICTION:")

        print(
            json.dumps(
                prediction_result,
                indent=4,
                default=str
            )
        )


        # ==================================================
        # 2. SHAP / XAI ANALYSIS
        # ==================================================

        print("\n[2] GENERATING SHAP/XAI EVIDENCE...")

        xai_result = explain_prediction(data)

        print("\nXAI EVIDENCE:")

        print(
            json.dumps(
                xai_result,
                indent=4,
                default=str
            )
        )


        # ==================================================
        # 3. CREATE INVESTIGATION STATE
        # ==================================================

        print("\n[3] CREATING INVESTIGATION STATE...")

        investigation_data = {

            "ml_prediction":
                prediction_result,

            "xai_evidence":
                xai_result,

            "network_flow":
                data

        }


        # ==================================================
        # 4. START AUTONOMOUS INVESTIGATION AGENT
        # ==================================================

        print("\n[4] STARTING AUTONOMOUS INVESTIGATION AGENT...")

        agent_result = agent.investigate(
            investigation_data
        )


        # ==================================================
        # 5. EXTRACT AGENT RESULTS
        # ==================================================

        investigation_report = agent_result.get(

            "report",

            "Investigation report was not generated."

        )


        investigation_steps = agent_result.get(

            "investigation_steps",

            []

        )


        evidence_evaluation = agent_result.get(

            "evidence_evaluation",

            {}

        )


        retrieved_evidence = agent_result.get(

            "retrieved_evidence",

            {}

        )


        agentic_status = agent_result.get(

            "agentic",

            False

        )


        agent_workflow = agent_result.get(

            "agent_workflow",

            {}

        )


        agent_decision = agent_workflow.get(

            "agent_decision",

            "UNKNOWN"

        )


        # ==================================================
        # 6. DISPLAY ACTUAL AGENT INVESTIGATION STEPS
        # ==================================================

        print("\n")
        print("=" * 70)
        print("AGENT INVESTIGATION STEPS")
        print("=" * 70)


        for step in investigation_steps:

            print(

                f"\nSTEP {step.get('step', '?')}: "
                f"{step.get('action', 'UNKNOWN')}"

            )

            print(

                step.get(
                    "description",
                    ""
                )

            )

            print(

                "Status:",
                step.get(
                    "status",
                    "UNKNOWN"
                )

            )


        # ==================================================
        # 7. DISPLAY AGENT DECISION
        # ==================================================

        print("\n")
        print("=" * 70)
        print("AGENT FINAL DECISION")
        print("=" * 70)

        print(

            agent_decision

        )


        # ==================================================
        # 8. DISPLAY SECURITY KNOWLEDGE
        # ==================================================

        print("\n")
        print("=" * 70)
        print("RETRIEVED SECURITY KNOWLEDGE")
        print("=" * 70)

        print(

            json.dumps(
                retrieved_evidence,
                indent=4,
                default=str
            )

        )


        # ==================================================
        # 9. DISPLAY EVIDENCE EVALUATION
        # ==================================================

        print("\n")
        print("=" * 70)
        print("EVIDENCE EVALUATION")
        print("=" * 70)

        print(

            json.dumps(
                evidence_evaluation,
                indent=4,
                default=str
            )

        )


        # ==================================================
        # 10. DISPLAY FINAL AI REPORT
        # ==================================================

        print("\n")
        print("=" * 70)
        print("FINAL AI INVESTIGATION REPORT")
        print("=" * 70)

        print(

            investigation_report

        )


        # ==================================================
        # 11. FINAL JSON RESPONSE
        # ==================================================

        return jsonify({

            "success": True,


            # ------------------------------------------------
            # NETWORK FLOW
            # ------------------------------------------------

            "network_flow":
                data,


            # ------------------------------------------------
            # XGBOOST ML PREDICTION
            # ------------------------------------------------

            "ml_prediction":
                prediction_result,


            # ------------------------------------------------
            # SHAP / XAI
            # ------------------------------------------------

            "xai_evidence":
                xai_result,


            # ------------------------------------------------
            # AGENTIC INVESTIGATION
            # ------------------------------------------------

            "agentic_investigation": {

                "enabled":
                    agentic_status,

                "final_decision":
                    agent_decision,

                "investigation_steps":
                    investigation_steps,

                "evidence_evaluation":
                    evidence_evaluation,

                "retrieved_security_knowledge":
                    retrieved_evidence,

                "workflow":
                    agent_workflow

            },


            # ------------------------------------------------
            # FINAL LLM REPORT
            # ------------------------------------------------

            "investigation_report":
                investigation_report

        })


    # ======================================================
    # ERROR HANDLING
    # ======================================================

    except Exception as e:

        print("\n")
        print("=" * 70)
        print("ERROR DURING CYBER ATTACK INVESTIGATION")
        print("=" * 70)

        traceback.print_exc()

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


# ==========================================================
# START FLASK SERVER
# ==========================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("AGENTIC CYBER ATTACK INVESTIGATION API")
    print("=" * 70)

    print("\nServer:")
    print("http://127.0.0.1:5001")

    print("\nEndpoints:")
    print("GET  /")
    print("GET  /health")
    print("POST /analyze")

    print("\nArchitecture:")
    print("Network Flow")
    print("      ↓")
    print("XGBoost")
    print("      ↓")
    print("SHAP / XAI")
    print("      ↓")
    print("Investigation Agent")
    print("      ↓")
    print("Agent Decision")
    print("      ↓")
    print("MITRE ATT&CK Retrieval")
    print("      ↓")
    print("Evidence Evaluation")
    print("      ↓")
    print("Llama Investigation Report")

    print("\n")

    app.run(

        host="127.0.0.1",

        port=5001,

        debug=True

    )