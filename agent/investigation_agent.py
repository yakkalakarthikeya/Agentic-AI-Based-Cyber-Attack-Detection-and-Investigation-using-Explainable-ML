import os
import sys
import json

# ==========================================================
# PROJECT PATH
# ==========================================================

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from llm.llm_client import LLMClient
from agent.tools import CyberInvestigationTools


class CyberInvestigationAgent:

    def __init__(self):

        # Llama / Groq client
        self.llm = LLMClient()

        # Agent tools
        self.tools = CyberInvestigationTools()

    # ==========================================================
    # MAIN INVESTIGATION FUNCTION
    # ==========================================================

    def investigate(self, investigation_data):

        ml_prediction = investigation_data.get(
            "ml_prediction",
            {}
        )

        xai_evidence = investigation_data.get(
            "xai_evidence",
            {}
        )

        network_flow = investigation_data.get(
            "network_flow",
            {}
        )

        # ======================================================
        # 1. EXTRACT ML INFORMATION
        # ======================================================

        prediction = ml_prediction.get(
            "prediction",
            "UNKNOWN"
        )

        attack_type = ml_prediction.get(
            "attack_type",
            prediction
        )

        confidence = ml_prediction.get(
            "confidence",
            0
        )

        classification_status = ml_prediction.get(
            "classification_status",
            "UNKNOWN"
        )

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0

        # ======================================================
        # AGENT INVESTIGATION LOG
        # ======================================================

        investigation_steps = []

        # ======================================================
        # STEP 1 — ANALYZE XAI
        # ======================================================

        print("\n")
        print("=" * 70)
        print("AGENT STEP 1: ANALYZING XAI EVIDENCE")
        print("=" * 70)

        xai_analysis = self.tools.analyze_xai(
            xai_evidence=xai_evidence,
            network_flow=network_flow
        )

        investigation_steps.append({

            "step": 1,

            "action": "ANALYZE_XAI",

            "description":
                "Agent analyzed the supplied SHAP/XAI evidence.",

            "status": "completed"

        })

        # ======================================================
        # STEP 2 — AGENT DECIDES WHETHER KNOWLEDGE IS NEEDED
        # ======================================================

        print("\n")
        print("=" * 70)
        print("AGENT STEP 2: DECIDING WHETHER ADDITIONAL KNOWLEDGE IS NEEDED")
        print("=" * 70)

        #
        # This is the agent's investigation policy.
        #
        # We use the ML result and evidence availability
        # to decide whether contextual cybersecurity
        # knowledge should be retrieved.
        #

        xai_available = bool(xai_evidence)

        knowledge_required = False

        decision_reason = ""

        if classification_status == "POSSIBLE_UNSEEN_ATTACK":

            knowledge_required = True

            decision_reason = (
                "The ML system indicates a possible unseen "
                "attack, so additional cybersecurity context "
                "is required."
            )

        elif confidence < 80:

            knowledge_required = True

            decision_reason = (
                "ML confidence is below the strong-confidence "
                "threshold, so additional cybersecurity "
                "context is required."
            )

        elif classification_status == "KNOWN" and xai_available:

            knowledge_required = True

            decision_reason = (
                "The attack is a known class and XAI evidence "
                "is available. The agent retrieves cybersecurity "
                "context to support the investigation."
            )

        else:

            knowledge_required = False

            decision_reason = (
                "The available evidence does not require "
                "additional cybersecurity knowledge at this stage."
            )

        print(
            "Knowledge required:",
            knowledge_required
        )

        print(
            "Decision reason:",
            decision_reason
        )

        investigation_steps.append({

            "step": 2,

            "action": "DECIDE_INVESTIGATION",

            "description":
                decision_reason,

            "knowledge_required":
                knowledge_required,

            "status":
                "completed"

        })

        # ======================================================
        # STEP 3 — SEARCH SECURITY KNOWLEDGE / MITRE
        # ======================================================

        print("\n")
        print("=" * 70)
        print("AGENT STEP 3: SECURITY KNOWLEDGE RETRIEVAL")
        print("=" * 70)

        retrieved_evidence = {}

        if knowledge_required:

            query = (
                f"Find cybersecurity context relevant to "
                f"{attack_type}. Provide only techniques and "
                f"attack characteristics supported by the "
                f"retrieved security knowledge."
            )

            retrieved_evidence = (
                self.tools.search_security_knowledge(

                    attack_type=str(
                        attack_type
                    ).lower().strip(),

                    query=query

                )
            )

            investigation_steps.append({

                "step": 3,

                "action":
                    "SEARCH_SECURITY_KNOWLEDGE",

                "description":
                    "Agent retrieved cybersecurity knowledge "
                    "relevant to the ML classification.",

                "status":
                    retrieved_evidence.get(
                        "status",
                        "completed"
                    )

            })

        else:

            retrieved_evidence = {

                "tool":
                    "SEARCH_SECURITY_KNOWLEDGE",

                "status":
                    "not_required",

                "message":
                    "Agent determined that additional "
                    "security knowledge was not required."

            }

            investigation_steps.append({

                "step": 3,

                "action":
                    "SEARCH_SECURITY_KNOWLEDGE",

                "description":
                    "Agent determined that security knowledge "
                    "retrieval was not required.",

                "status":
                    "skipped"

            })

        # ======================================================
        # STEP 4 — EVALUATE EVIDENCE
        # ======================================================

        print("\n")
        print("=" * 70)
        print("AGENT STEP 4: EVALUATING EVIDENCE")
        print("=" * 70)

        evidence_evaluation = (
            self.tools.evaluate_evidence(

                ml_prediction=
                    ml_prediction,

                xai_evidence=
                    xai_evidence,

                retrieved_evidence=
                    retrieved_evidence

            )
        )

        evidence_sufficient = (
            evidence_evaluation.get(
                "evidence_sufficient",
                False
            )
        )

        if evidence_sufficient:

            agent_decision = (
                "SUFFICIENT_EVIDENCE"
            )

        else:

            agent_decision = (
                "INSUFFICIENT_EVIDENCE"
            )

        investigation_steps.append({

            "step": 4,

            "action":
                "EVALUATE_EVIDENCE",

            "description":
                "Agent evaluated ML, XAI and retrieved "
                "security evidence.",

            "evidence_sufficient":
                evidence_sufficient,

            "status":
                "completed"

        })

        # ======================================================
        # STEP 5 — FINAL AGENT DECISION
        # ======================================================

        print("\n")
        print("=" * 70)
        print("AGENT STEP 5: FINAL INVESTIGATION DECISION")
        print("=" * 70)

        print(
            "Agent decision:",
            agent_decision
        )

        investigation_steps.append({

            "step": 5,

            "action":
                "FINAL_INVESTIGATION_DECISION",

            "description":
                "Agent completed the investigation and "
                "prepared the evidence for final reporting.",

            "decision":
                agent_decision,

            "status":
                "completed"

        })

        # ======================================================
        # PREPARE AGENT WORKFLOW
        # ======================================================

        agent_workflow = {

            "ml_detection":
                ml_prediction,

            "xai_analysis":
                xai_analysis,

            "knowledge_retrieval":
                retrieved_evidence,

            "evidence_evaluation":
                evidence_evaluation,

            "agent_decision":
                agent_decision

        }

        # ======================================================
        # FINAL REPORT PROMPT
        # ======================================================

        prompt = f"""
You are the final reporting component of an
Agentic AI cybersecurity investigation system.

The system has already completed an investigation.

Your job is ONLY to generate a clear final
cybersecurity investigation report from the
ACTUAL evidence and ACTUAL agent workflow supplied below.

==================================================
ML DETECTION
==================================================

{json.dumps(
    ml_prediction,
    indent=4,
    default=str
)}

==================================================
XAI ANALYSIS
==================================================

{json.dumps(
    xai_analysis,
    indent=4,
    default=str
)}

==================================================
SECURITY KNOWLEDGE RETRIEVED BY THE AGENT
==================================================

{json.dumps(
    retrieved_evidence,
    indent=4,
    default=str
)}

==================================================
EVIDENCE EVALUATION
==================================================

{json.dumps(
    evidence_evaluation,
    indent=4,
    default=str
)}

==================================================
AGENT INVESTIGATION STEPS
==================================================

{json.dumps(
    investigation_steps,
    indent=4,
    default=str
)}

==================================================
AGENT DECISION
==================================================

{agent_decision}

==================================================
NETWORK FLOW
==================================================

{json.dumps(
    network_flow,
    indent=4,
    default=str
)}

==================================================
CRITICAL REPORTING RULES
==================================================

1. The ML model is the primary classifier.

2. NEVER change the ML prediction.

3. SHAP/XAI explains the ML model's prediction.

4. MITRE/security knowledge provides contextual
   information only.

5. Do NOT claim that a MITRE technique was observed
   in the network traffic unless the supplied evidence
   explicitly says so.

6. Do NOT invent MITRE techniques.

7. Do NOT invent packet behavior.

8. Do NOT invent authentication activity.

9. Do NOT claim that credentials were guessed unless
   authentication evidence is actually available.

10. A high ML confidence does NOT automatically mean
    the real-world attack is confirmed.

11. Clearly distinguish:
       ML classification
       XAI evidence
       Agent investigation
       MITRE context
       Final assessment

12. If only one network flow is available, mention
    that as a limitation.

13. Recommended actions must be defensive.

14. Do not provide offensive attack instructions.

15. Only describe agent actions that actually appear
    in the AGENT INVESTIGATION STEPS.

16. If MITRE retrieval returned no specific knowledge,
    clearly state that.

==================================================
RETURN EXACTLY THIS FORMAT
==================================================

# AI INVESTIGATION REPORT

## 1. ML DETECTION

Give:

- Attack prediction
- ML confidence
- Classification status

Use exactly the supplied ML prediction.

---

## 2. WHY DID THE ML MODEL DETECT IT?

Explain the important XAI/SHAP features.

Use only the supplied XAI evidence.

Do not invent explanations that require information
not present in the evidence.

---

## 3. XAI EVIDENCE

List the most important features using:

Feature → Value → SHAP contribution

Keep this concise.

Explain that these features influenced the ML
model's prediction.

Do not say that SHAP independently proves the attack.

---

## 4. AGENT INVESTIGATION

Briefly explain what the investigation agent did.

Do NOT list individual steps.

Write this as one concise paragraph explaining that:

- The agent analyzed the XAI evidence.
- The agent decided whether additional cybersecurity
  knowledge was required.
- If required, the agent retrieved relevant security
  knowledge from the available knowledge source.
- The agent evaluated the available ML, XAI, and
  retrieved evidence.
- The agent produced a final evidence assessment.

Then provide:

**Agent Decision:** [actual agent decision]

Only describe actions that actually occurred.
Do not invent agent actions.

Do not claim that the agent performed an action
that is not present in the investigation steps.

---

## 5. MITRE ATT&CK / SECURITY CONTEXT

Only report techniques or cybersecurity information
that actually appears inside the retrieved evidence.

For each retrieved technique provide:

- Technique ID
- Technique name
- Brief relevance

IMPORTANT:

Say clearly that MITRE ATT&CK provides contextual
knowledge and does not independently prove that the
observed traffic is malicious.

If no specific knowledge was retrieved, write:

"No specific MITRE/security knowledge was retrieved
for this investigation."

---

## 6. EVIDENCE EVALUATION

Show:

ML Evidence: Available / Not Available

XAI Evidence: Available / Not Available

Security Knowledge: Available / Not Available

Overall Evidence:
SUFFICIENT / INSUFFICIENT

Then briefly explain why.

Do not use the word "confirmed" unless the supplied
evidence genuinely supports confirmation.

---

## 7. FINAL ASSESSMENT

Give a short and clear final assessment.

Use this type of wording:

"The ML model classified the traffic as
[ATTACK] with [CONFIDENCE]% confidence.
The XAI evidence identifies the features that
influenced this classification. The retrieved
security knowledge provides relevant cybersecurity
context. Therefore, the available evidence
supports the ML classification, while additional
evidence may be required for real-world confirmation."

Adapt this to the actual evidence.

---

## 8. RECOMMENDED INVESTIGATION ACTIONS

Give 4–6 defensive actions based only on the
observed attack classification and available evidence.

Examples:

- Review relevant logs.
- Correlate additional network flows.
- Identify the destination service.
- Monitor the source.
- Review authentication activity if applicable.
- Apply defensive controls if malicious behavior
  is confirmed.

Do not provide offensive instructions.

---

## 9. UNCERTAINTY AND LIMITATIONS

Mention only actual limitations.

Examples:

- Single-flow analysis
- Missing authentication logs
- Missing payload information
- Unknown destination service
- Low confidence
- Missing features
- Insufficient evidence

If no major uncertainty exists, say:

"No major uncertainty was identified in the supplied
ML/XAI evidence, although additional traffic and
system logs can improve investigation confidence."

==================================================
FINAL REQUIREMENT
==================================================

The final report must be concise and easy to understand.

Do NOT create unsupported claims.

Do NOT add unrelated MITRE techniques.

Do NOT turn MITRE context into proof.

Do NOT make the LLM appear to have performed an action
that the Agent did not actually perform.

The report must clearly show:

ML Detection
      ↓
XAI Explanation
      ↓
Agent Investigation
      ↓
Security Knowledge
      ↓
Evidence Evaluation
      ↓
Final Assessment
"""

        # ======================================================
        # CALL LLAMA
        # ======================================================

        print("\n")
        print("=" * 70)
        print("GENERATING FINAL AI INVESTIGATION REPORT")
        print("=" * 70)

        response = self.llm.client.chat.completions.create(

            model=self.llm.model,

            messages=[

                {
                    "role": "system",

                    "content": (
                        "You are a cybersecurity "
                        "investigation reporting assistant. "
                        "Use only supplied evidence. "
                        "Never invent observations, "
                        "MITRE techniques, or attack activity."
                    )

                },

                {
                    "role": "user",

                    "content": prompt

                }

            ],

            temperature=0.0,

            max_tokens=1800

        )

        final_report = (
            response
            .choices[0]
            .message
            .content
        )

        # ======================================================
        # RETURN COMPLETE AGENT RESULT
        # ======================================================

        return {

            "report":
                final_report,

            "investigation_steps":
                investigation_steps,

            "evidence_evaluation":
                evidence_evaluation,

            "retrieved_evidence":
                retrieved_evidence,

            "agentic":
                True,

            "agent_workflow":
                agent_workflow

        }