import json
import os
from groq import Groq
from app.state.claim_state import VerisState
from app.database.audit import log_audit_event
from dotenv import load_dotenv
VALID_NEXT_AGENTS = {"fraud", "coverage", "finish", "escalate", "process"}


load_dotenv()
# 2. Update Environment Variables & Model Configs
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Llama 3.3 70B is great for high-accuracy structure handling, 
# or use llama-3.1-8b-instant if you want ultra-low latency routing.
GROQ_MODEL = "llama-3.3-70b-versatile" 

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

ROUTER_SYSTEM_PROMPT = """You are a routing component in an insurance claims pipeline. Given the current state of a claim, decide which agent should run next.

Available agents:
- "process": send the claim back for document re-processing (use this if critical fields are missing or document review failed)
- "fraud": run fraud detection (use this if fraud has not yet been assessed)
- "coverage": run coverage matching (use this if coverage has not yet been checked)
- "escalate": send the claim to a human reviewer (use this if something looks wrong, inconsistent, or outside what this pipeline should decide automatically)
- "finish": all necessary checks are complete and the claim is ready for a final decision

Respond with ONLY a JSON object in this exact shape, no other text:
{"next_agent": "<one of: process, fraud, coverage, escalate, finish>", "reasoning": "<one or two sentences explaining the choice>"}
"""

FINALIZE_SYSTEM_PROMPT = """You are the final decision component in an insurance claims pipeline. All required checks — document review, fraud detection, and coverage matching — have already been completed for this claim. Based on the information below, decide whether to approve or deny the claim.

Respond with ONLY a JSON object in this exact shape, no other text:
{"decision": "<one of: approved, denied>", "reasoning": "<two or three sentences explaining the decision, referencing the specific evidence that drove it>"}
"""

# Keep your prompt builders exactly as they are
def build_router_prompt(state: VerisState) -> str:
    context = {
        "claim_type": state.get("claim_type"),
        "claimed_amount": state.get("claimed_amount"),
        "incident_date": state.get("incident_date"),
        "extracted_fields": state.get("extracted_fields"),
        "document_review_summary": [
            {"filename": r.get("filename"), "status": r.get("status")}
            for r in (state.get("ai_document_review") or [])
        ],
        "fraud_score": state.get("fraud_score"),
        "fraud_signals": state.get("fraud_signals"),
        "coverage_matched": state.get("coverage_matched"),
        "coverage_exceptions": state.get("coverage_exceptions"),
        "current_stage": state.get("current_stage"),
    }
    return f"Claim state:\n{json.dumps(context, default=str)}\n\nWhich agent should run next?"

def build_finalize_prompt(state: VerisState) -> str:
    context = {
        "claim_type": state.get("claim_type"),
        "claimed_amount": state.get("claimed_amount"),
        "incident_date": state.get("incident_date"),
        "extracted_fields": state.get("extracted_fields"),
        "fraud_score": state.get("fraud_score"),
        "fraud_signals": state.get("fraud_signals"),
        "coverage_matched": state.get("coverage_matched"),
        "coverage_reasoning": state.get("coverage_reasoning"),
        "coverage_exceptions": state.get("coverage_exceptions"),
    }
    return f"Claim state:\n{json.dumps(context, default=str)}\n\nWhat is the final decision?"


# 3. Swap out the private LLM wrapper for Groq's ChatCompletion API
def _call_groq(system_prompt: str, user_prompt: str) -> dict:
    if not _client:
        raise RuntimeError("GROQ_API_KEY is not set")

    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        # Forces the model to respond strictly in a valid JSON schema container
        response_format={"type": "json_object"}, 
        temperature=0.0, # Zero temperature is vital for consistent state routing
    )

    return json.loads(response.choices[0].message.content)


# 4. Your node functions remain functionally identical (just call _call_groq)
def finalize_decision(state: VerisState) -> VerisState:
    prompt = build_finalize_prompt(state)
    try:
        raw_output = _call_groq(FINALIZE_SYSTEM_PROMPT, prompt)
        decision = raw_output.get("decision")
        reasoning = raw_output.get("reasoning", "")

        if decision not in {"approved", "denied"}:
            raise ValueError(f"Model returned invalid decision: {decision!r}")
    except Exception as e:
        decision = "escalated"
        reasoning = f"Final decision failed, escalating for manual review. Error: {e}"
        print(f"Finalize error: {e}")

    state["decision"] = decision
    state["decision_reasoning"] = reasoning

    log_audit_event(
        state,
        stage="final_decision",
        note=f"Final decision: '{decision}'",
        agent_model=GROQ_MODEL,
        result={"decision": decision},
        reasoning=reasoning,
    )
    state["current_stage"] = "final_decision"
    return state


def route_decision(state: VerisState) -> VerisState:
    prompt = build_router_prompt(state)
    try:
        raw_output = _call_groq(ROUTER_SYSTEM_PROMPT, prompt)
        next_agent = raw_output.get("next_agent")
        routing_reasoning = raw_output.get("reasoning", "")

        if next_agent not in VALID_NEXT_AGENTS:
            raise ValueError(f"Model returned invalid next_agent: {next_agent!r}")
    except Exception as e:
        next_agent = "escalate"
        routing_reasoning = f"Routing failed, escalating for manual review. Error: {e}"
        print(f"Router error: {e}")

    state["next_agent"] = next_agent

    log_audit_event(
        state,
        stage="routing",
        note=f"Routed to '{next_agent}'",
        agent_model=GROQ_MODEL,
        result={"next_agent": next_agent},
        reasoning=routing_reasoning,
    )
    state["current_stage"] = "routing"

    if next_agent == "escalate":
        state["decision"] = "escalated"
        state["decision_reasoning"] = routing_reasoning
    elif next_agent == "finish":
        state = finalize_decision(state)

    return state