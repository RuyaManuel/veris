# Veris Engine

Automated, local-first multi-agent orchestration for insurance claims processing.

Veris is an autonomous pipeline designed to accelerate insurance workflows by coordinating specialized AI nodes. The system automatically ingests claims data, extracts document insights, and uses a central decision matrix to route files through fraud analysis and coverage verification without human bottlenecking.

---

## Workflow Architecture

The engine coordinates the claims processing lifecycle by passing the transaction context through specialized agent nodes:

           [ Intake ]
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

## Core Stack

The automation pipeline relies on these primary backend tools:

* **LangGraph:** Orchestrates the multi-agent execution loop and transition routes.
* **Moondream & Torch:** Handles secure, localized vision processing for claims paperwork.
* **Groq & LLM Clients:** Powers the intelligence behind the Decision routing node.
* **Supabase:** Contextual storage and historical policy lookup layer.
* **Pydantic:** Validates incoming user inputs at the pipeline entrance.

---

## Documentation & Help

Please visit the documentation for complete integration guides, system design parameters, and deployment specifications.

---

## Security Policy

To report a security vulnerability or bug, please refer to our project security guidelines.