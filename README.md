# Veris Engine

Automated, local-first multi-agent orchestration for insurance claims processing.

Veris is an autonomous pipeline designed to accelerate insurance workflows by coordinating specialized AI nodes. The system automatically ingests claims data, extracts document insights, and uses a central decision matrix to route files through fraud analysis and coverage verification without human bottlenecking.

---

## Workflow Architecture

The engine coordinates the claims processing lifecycle by passing the transaction context through specialized agent nodes:

    [ Intake / BuildParams ]
               │
               ▼
       [ Process Node ] ──► (Local Vision & OCR Document Review)
               │
               ▼
       [ Decision Node ] ◄─ (Central Router / Guardrail Evaluation)
               │
      ┌────────┼────────┬────────┐
      ▼        ▼        ▼        ▼
  [Fraud]  [Coverage] [Escalate] [Finish]

---

## Help

See the documentation for complete integration guides, system design parameters, and deployment specs.

---

## Installation

Install the required system frameworks and local machine learning clients using pip:

```bash
pip install -r requirements.txt

```

---

## A Simple Example

```python
from app.claims_state import BuildParams, build_claim_state

# 1. Package raw incoming claim payload parameters
params = BuildParams(
    claimant_id="usr_992384x",
    policy_id="pol_88301df",
    claimant_statement="Vehicle sustained front bumper impact during parking maneuver."
)

# 2. Initialize the automated multi-agent workflow
claim_state = build_claim_state(params)

print(claim_state)
#> {'claim_id': 'clm_01hj83...', 'current_stage': 'process', 'process_attempt': 0, ...}

print(claim_state["current_stage"])
#> process

```

---

## Core Core Stack

The automation pipeline relies on these primary backend tools:

* **LangGraph:** Orchestrates the multi-agent execution loop and transition routes.
* **Moondream & Torch:** Handles secure, localized vision processing for claims paperwork.
* **Groq & LLM Clients:** Powers the intelligence behind the Decision routing node.
* **Supabase:** Contextual storage and historical policy lookup layer.
* **Pydantic:** Validates incoming user inputs at the pipeline entrance.

---

## Security Policy

To report a security vulnerability or bug, please refer to our project security guidelines.

```

```