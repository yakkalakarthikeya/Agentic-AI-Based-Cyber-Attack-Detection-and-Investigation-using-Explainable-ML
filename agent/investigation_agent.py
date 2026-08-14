import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from llm.llm_client import LLMClient


class CyberInvestigationAgent:

    def __init__(self):
        self.llm = LLMClient()

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

        llm_required = ml_prediction.get(
            "llm_required",
            False
        )

        prompt = f"""
You are a cybersecurity investigation assistant
inside an AI-based cyber attack investigation platform.

The system uses an ML model for known attack
classification and a Groq LLM for deeper investigation
when the ML prediction is uncertain or potentially
represents an unseen attack.

==================================================
ML PREDICTION
==================================================

{ml_prediction}

==================================================
XAI EVIDENCE
==================================================

{xai_evidence}

==================================================
NETWORK FLOW
==================================================

{network_flow}

==================================================
IMPORTANT ARCHITECTURE RULES
==================================================

The ML model is responsible for identifying known
attack classes.

The current ML prediction is:

{prediction}

The ML confidence is:

{confidence}%

The classification status is:

{classification_status}

LLM required:

{llm_required}

--------------------------------------------------
CASE 1: KNOWN ATTACK
--------------------------------------------------

If classification_status is "KNOWN" and the prediction
is an attack:

- Treat the ML prediction as the detected attack.
- Do NOT replace the ML prediction.
- Use XAI evidence to explain the prediction.
- Do not introduce another attack as the detected attack.
- Explain the network-flow characteristics using only
  the supplied evidence.

--------------------------------------------------
CASE 2: NORMAL TRAFFIC
--------------------------------------------------

If the ML prediction is BENIGN or NORMAL:

- Treat the traffic as normal.
- Do not invent an attack.
- Explain why the model considers the traffic benign.
- Mention limitations if confidence is low.

--------------------------------------------------
CASE 3: POSSIBLE UNSEEN ATTACK
--------------------------------------------------

If classification_status is
"POSSIBLE_UNSEEN_ATTACK":

The ML model is uncertain about the exact attack type.

In this case, investigate the supplied:

- ML probabilities
- confidence
- probability margin
- XAI evidence
- network-flow characteristics

You MAY identify a possible attack type that could
explain the observed behavior.

However:

- Do NOT claim that the unseen attack is confirmed.
- Use terms such as "possible", "potential",
  "candidate", or "requires further investigation".
- Do not invent evidence.
- Do not pretend the ML model classified the unseen
  attack.
- Clearly distinguish the ML prediction from the
  LLM's investigation hypothesis.

The LLM is an investigation and reasoning component,
not the ground-truth classifier.

==================================================
SECURITY RULES
==================================================

1. Never invent evidence.

2. Never claim an attack is confirmed without evidence.

3. Clearly distinguish ML prediction from LLM analysis.

4. If confidence is low, explicitly state that.

5. If the evidence is insufficient, state that.

6. Use XAI evidence to support explanations.

7. Do not provide offensive attack instructions.

8. Recommended actions must be defensive.

==================================================
RETURN EXACTLY THESE SECTIONS
==================================================

## 1. ML DETECTION

State exactly what the ML model predicted.

## 2. CONFIDENCE

State the ML confidence and explain whether it is
high, moderate, or low.

## 3. ATTACK STATUS

State whether the traffic is:

- NORMAL
- KNOWN ATTACK
- POSSIBLE UNSEEN ATTACK

Do not confuse these categories.

## 4. INVESTIGATION SUMMARY

Explain what the ML model detected and summarize
the evidence.

## 5. XAI EVIDENCE

Explain the important XAI features and their
contribution to the ML result.

## 6. POSSIBLE ATTACK TYPE

If the ML prediction is a known attack, state that
known attack.

If the traffic is potentially an unseen attack,
provide the most plausible attack type as an
INVESTIGATION HYPOTHESIS only.

If the evidence is insufficient, state:

"Unable to determine a possible unseen attack from
the available evidence."

## 7. SEVERITY

Give an appropriate severity:

LOW
MEDIUM
HIGH
CRITICAL

Explain the reasoning.

## 8. WHY THIS TRAFFIC IS SUSPICIOUS OR NORMAL

Explain the network-flow characteristics using only
the supplied evidence.

## 9. RECOMMENDED INVESTIGATION STEPS

Provide defensive investigation steps appropriate
to the detected or suspected behavior.

## 10. UNKNOWN OR UNCERTAIN BEHAVIOR

Clearly identify:

- low confidence
- conflicting probabilities
- weak XAI evidence
- missing features
- possible unseen attack
- other limitations

Do not hide uncertainty.

==================================================
FINAL RULE
==================================================

If the ML model predicts a known attack with strong
confidence, do not replace it.

If the ML model is uncertain and the classification
status is POSSIBLE_UNSEEN_ATTACK, you may investigate
a possible unseen attack, but clearly label it as an
LLM-generated hypothesis and NOT a confirmed
classification.
"""

        response = self.llm.client.chat.completions.create(
            model=self.llm.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a cybersecurity "
                        "investigation assistant. "
                        "The ML model handles known "
                        "classification. When the ML "
                        "model is uncertain, investigate "
                        "possible unseen attacks using "
                        "only the supplied evidence. "
                        "Never present an LLM hypothesis "
                        "as confirmed ground truth."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0,
            max_tokens=1500
        )

        return response.choices[0].message.content