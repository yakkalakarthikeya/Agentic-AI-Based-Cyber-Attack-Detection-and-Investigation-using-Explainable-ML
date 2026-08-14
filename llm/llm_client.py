import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class LLMClient:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=api_key
        )

        self.model = "llama-3.3-70b-versatile"

    def investigate(self, investigation_data):

        prompt = f"""
You are a cybersecurity investigation assistant
working inside an AI-based cyber attack investigation platform.

The machine-learning model is the primary attack detector.

Your job is to investigate and explain the detection using:

1. ML prediction
2. Prediction confidence
3. XAI feature contributions
4. Network-flow characteristics

IMPORTANT RULES:

- Do not invent evidence.
- Do not claim an unknown attack is confirmed.
- If confidence is low, explicitly state that the prediction is uncertain.
- Explain why the ML model may have produced the prediction.
- Use the supplied XAI evidence.
- Keep the report technically accurate.
- Do not provide offensive attack instructions.

Detection information:

{investigation_data}

Return the investigation report using exactly these sections:

1. DETECTED ATTACK
2. CONFIDENCE
3. INVESTIGATION SUMMARY
4. XAI EVIDENCE
5. SEVERITY
6. WHY THIS TRAFFIC MATCHES
7. RECOMMENDED INVESTIGATION STEPS
8. UNKNOWN OR UNCERTAIN BEHAVIOR

Keep the report concise but informative.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a cybersecurity "
                        "investigation assistant."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=1200
        )

        return response.choices[0].message.content