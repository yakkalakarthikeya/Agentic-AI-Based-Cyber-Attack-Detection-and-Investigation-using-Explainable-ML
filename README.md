# 🛡️ Agentic AI-Based Cyber Attack Detection and Investigation using Explainable ML

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-blue">
  <img alt="Flask" src="https://img.shields.io/badge/Flask-Backend-black">
  <img alt="XGBoost" src="https://img.shields.io/badge/Model-XGBoost-orange">
  <img alt="SHAP" src="https://img.shields.io/badge/Explainability-SHAP-green">
  <img alt="LLM" src="https://img.shields.io/badge/Agent-Groq%20LLM-purple">
  <img alt="Status" src="https://img.shields.io/badge/Status-Active%20Development-yellow">
</p>

An end-to-end **agentic cybersecurity framework** that captures live network traffic, classifies it into attack categories with **XGBoost**, explains every prediction with **SHAP**, and hands the evidence to an **AI investigation agent** (powered by a Groq-hosted LLM) that reasons over the evidence and produces a structured, human-readable incident report — no black-box verdicts, no manual triage.

> Instead of just flagging "malicious," the system explains **why**, retrieves relevant security context, and writes an analyst-style investigation report automatically.

---

## 📑 Table of Contents

- [Motivation](#-motivation)
- [Key Features](#-key-features)
- [Architecture / Pipeline](#️-architecture--pipeline)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Dataset](#-dataset)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [How the Investigation Agent Works](#-how-the-investigation-agent-works)
- [Results](#-results)
- [Screenshots](#-screenshots)
- [Limitations](#-limitations)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [FAQ / Troubleshooting](#-faq--troubleshooting)
- [Acknowledgments](#-acknowledgments)
- [Author](#-author)
- [License](#-license)

---

## 🎯 Motivation

Traditional Intrusion Detection Systems (IDS) are good at flagging traffic as malicious but give security analysts no context on *why* a flow was flagged or *what it means operationally*. This creates two problems:

1. **Trust gap** — analysts don't trust a black-box verdict without evidence.
2. **Triage bottleneck** — even correct detections still require a human to manually write up what happened, correlate it with known attack patterns, and decide next steps.

This project closes both gaps by pairing a high-accuracy detector with an **explainability layer** (SHAP) and an **agentic LLM layer** that turns raw evidence into a structured investigation report automatically — essentially compressing "detect → explain → investigate → report" into a single API call.

---

## ✨ Key Features

- **Self-generated, labeled dataset** (`flask_lab`) — a Flask target app produces both normal and controlled attack traffic in a lab environment, so the training data isn't a reused public dataset.
- **Traffic capture & flow-based feature extraction** (`capture`, `features`) — raw packets/traffic are converted into structured, model-ready flow features.
- **ML-based detection** (`models`, `prediction`) — an XGBoost classifier detects and categorizes traffic across **5 attack classes**.
- **Explainability layer** (`xai`) — SHAP explains *why* the model made a given prediction at the feature level, rather than returning a single opaque label.
- **Agentic investigation** (`agent`, `llm`) — an AI agent consumes the ML prediction + SHAP evidence, performs tool selection and evidence evaluation, retrieves relevant context via RAG over cybersecurity knowledge, and produces a structured report through a Groq-hosted LLM.
- **Single-call REST API** (`api.py`) — `POST /analyze` runs the entire pipeline end-to-end: raw flow in → prediction + explanation + investigation report out.
- **Dashboard** (`dashboard`) — a front-end for visualizing detections, evidence, and generated reports.

---

## 🏗️ Architecture / Pipeline

```
 Flask Lab (normal + attack traffic)
            │
            ▼
   Traffic Capture → Flow Feature Extraction
            │
            ▼
      XGBoost Classifier  ──►  ML Prediction (attack class)
            │
            ▼
       SHAP Explainer  ──►  XAI Evidence (feature attributions)
            │
            ▼
   AI Investigation Agent (tool selection + evidence evaluation)
            │
            ▼
   RAG over Cybersecurity Knowledge Base
            │
            ▼
     Groq-hosted LLM  ──►  Structured Investigation Report
            │
            ▼
        Dashboard / API JSON Response
```

Everything is orchestrated by `api.py`, which exposes a single `/analyze` endpoint that runs prediction → explanation → investigation in one synchronous call and returns all three artifacts together.

---

## 🧰 Tech Stack

| Layer | Tools |
|---|---|
| Backend / API | Python, Flask, Flask-CORS |
| Detection | XGBoost |
| Explainability | SHAP |
| Agent / Reasoning | Custom investigation agent, tool selection, evidence evaluation |
| Knowledge Retrieval | RAG over a cybersecurity knowledge base |
| LLM | Groq-hosted LLM |
| Lab / Traffic Generation | Flask (`flask_lab`) |
| Frontend | `dashboard` (see folder for its specific stack) |

---

## 📁 Project Structure

```
├── agent/            # Investigation agent logic (tool selection, evidence evaluation)
├── capture/           # Network traffic capture utilities
├── dashboard/          # Front-end for visualizing detections & reports
├── data/              # Generated / labeled traffic datasets
├── features/           # Flow-based feature extraction
├── flask_lab/          # Target Flask app for generating normal + attack traffic
├── llm/               # LLM integration (Groq) + RAG components
├── models/             # Trained XGBoost model artifacts
├── prediction/          # Model inference logic (predict_attack)
├── xai/                # SHAP-based live explainer
├── api.py             # Main Flask API — orchestrates the full pipeline
└── .gitignore
```

---

## 📊 Dataset

The dataset is **self-generated**, not pulled from a public benchmark (e.g. NSL-KDD or CICIDS). Traffic is produced by the `flask_lab` target app under controlled conditions:

| Item | Detail |
|---|---|
| Traffic classes | Normal + **5 attack classes** *(list your specific attack types here, e.g. DoS, port scan, brute force, SQL injection, XSS)* |
| Generation method | `flask_lab` target app, traffic captured via `capture/` |
| Feature extraction | Flow-based features via `features/` |
| Labeling | Controlled/simulated, so ground truth is known at generation time |
| Size | *(fill in: number of flows/samples per class)* |

> Fill in the exact attack categories and sample counts here — this is the section reviewers and recruiters look at first to judge dataset rigor.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip / virtualenv
- A [Groq API key](https://console.groq.com) for the LLM-based investigation agent

### 1. Clone the repository

```bash
git clone https://github.com/yakkalakarthikeya/Agentic-AI-Based-Cyber-Attack-Detection-and-Investigation-using-Explainable-ML.git
cd Agentic-AI-Based-Cyber-Attack-Detection-and-Investigation-using-Explainable-ML
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> If `requirements.txt` isn't committed yet, install the core stack manually:
> ```bash
> pip install flask flask-cors xgboost shap pandas numpy scikit-learn groq
> ```

### 3. Set environment variables

Create a `.env` file (or export directly) with your LLM credentials:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Generate lab traffic (optional — to rebuild the dataset)

```bash
cd flask_lab
python app.py
```
Use this target app to generate normal and controlled attack traffic, which is captured via the `capture/` scripts and turned into flow features via `features/`.

### 5. Train the model (optional — if not using the pretrained artifact in `models/`)

```bash
cd models
python train.py   # replace with your actual training script name
```

### 6. Run the main API

```bash
python api.py
```
The API starts at `http://127.0.0.1:5001`.

### 7. Run the dashboard (optional)

```bash
cd dashboard
# follow the setup instructions inside dashboard/ for its specific stack
```

---

## 🔌 API Reference

### `GET /`
Health/info endpoint — returns API status and available routes.

### `GET /health`
Simple health check.

### `POST /analyze`
Runs the full pipeline on a network flow: **ML prediction → SHAP explanation → agentic investigation report**.

**Request body:** JSON object describing a network flow (feature values matching what the model was trained on).

**Example:**
```bash
curl -X POST http://127.0.0.1:5001/analyze \
  -H "Content-Type: application/json" \
  -d '{ "...flow_features...": "..." }'
```

**Response:**
```json
{
  "success": true,
  "ml_prediction": {
    "attack_class": "...",
    "confidence": 0.0
  },
  "xai_evidence": {
    "top_features": ["...", "..."],
    "shap_values": { "...": "..." }
  },
  "investigation_report": "Structured analyst-style write-up generated by the LLM agent..."
}
```

---

## 🧠 How the Investigation Agent Works

1. **Receives evidence** — the ML prediction and SHAP feature attributions for the flagged flow.
2. **Selects tools/context** — decides which knowledge sources are relevant for the specific attack type.
3. **Retrieves context (RAG)** — pulls supporting information from a cybersecurity knowledge base to ground the report in real security context rather than the LLM's own assumptions.
4. **Synthesizes the report** — the Groq-hosted LLM combines the ML verdict, the SHAP evidence, and the retrieved context into a structured, analyst-style investigation report (what happened, why the model flagged it, and what it means).

---

## 📈 Results

*(Fill in once you have final numbers — this section matters most for anyone evaluating the project.)*

| Metric | Value |
|---|---|
| Accuracy | — |
| Precision / Recall / F1 (per class) | — |
| Attack classes covered | 5 |
| Inference latency (`/analyze`) | — |

---

## 🖼️ Screenshots

*(Add dashboard screenshots or a sample investigation report output here once available — this significantly improves the README's impact.)*

```
![Dashboard](docs/screenshots/dashboard.png)
![Sample Report](docs/screenshots/report.png)
```

---

## ⚠️ Limitations

- Trained on lab-generated traffic (`flask_lab`), not real-world/production network traffic — generalization to live networks is untested.
- Currently limited to 5 attack classes.
- LLM-generated reports depend on the retrieved RAG context and are only as good as the underlying knowledge base.
- Single-machine lab setup (no distributed capture or high-throughput handling yet).

---

## 🗺️ Roadmap

- [ ] Expand beyond 5 attack classes
- [ ] Validate against public benchmark datasets (e.g. CICIDS2017/2018)
- [ ] Add automated response / mitigation suggestions
- [ ] Containerize the full pipeline (Docker)
- [ ] Add authentication to the API
- [ ] Publish evaluation metrics and a model card

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a Pull Request

---

## ❓ FAQ / Troubleshooting

**The API can't reach the LLM agent.**
Check that `GROQ_API_KEY` is set correctly in your environment.

**CORS errors when calling `/analyze` from a browser.**
`api.py` currently only allows `http://127.0.0.1:5002` and `http://localhost:5002` as origins — update the `CORS` config in `api.py` if your dashboard runs on a different port.

**`/analyze` returns a 500 error.**
Check the console output — the API prints the full ML prediction, XAI evidence, and traceback on failure to help pinpoint whether the issue is in prediction, explanation, or the investigation agent.

---

## 🙏 Acknowledgments

- [XGBoost](https://xgboost.readthedocs.io/) for the classification backbone
- [SHAP](https://shap.readthedocs.io/) for model explainability
- [Groq](https://groq.com/) for LLM inference powering the investigation agent

---

## 👤 Author

**Y. Karthikeya** ([@yakkalakarthikeya](https://github.com/yakkalakarthikeya))
B.Tech, Artificial Intelligence & Data Science — Amrita School of AI, Amrita Vishwa Vidyapeetham, Coimbatore

---

