from typing import TypedDict, Literal, Optional
import uuid
from datetime import datetime, timezone


class ClaimState(TypedDict):
    # Claim identity
    claim_id: str
    submitted_at: str                          # ISO string — safe to serialize
    policy_id: str
    claimant_id: str
    raw_documents: list[dict]  # multiple raw documents each requiring extensive metadata definition.


    # Decision making agent data
    next_agent: Optional[Literal["fraud", "coverage", "audit"]]
    decision_reasoning: str

    # Document Organising agent
    claim_type: Optional[str]
    claimed_amount: Optional[float]
    incident_date: Optional[str]
    extracted_fields: Optional[dict]

    # Coverage agent output
    coverage_matched: Optional[bool]
    coverage_reasoning: Optional[str]
    coverage_exceptions: Optional[list[dict]]

    # Fraud agent output
    fraud_score: Optional[float]
    fraud_signals: Optional[list[str]]

    # Decision agent output
    decision: Optional[Literal["approved", "denied", "escalated"]]
    decision_reasoning: Optional[str]

    # Audit
    audit_trail: list[dict]                    # append-only, never overwrite
    current_stage: str


def create_claim(raw_documents: list[dict],claimant_id: str,policy_id: str) -> ClaimState:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "claim_id": str(uuid.uuid4()),
        "submitted_at": now,
        "claimant_id" : claimant_id,
        "raw_documents": raw_documents,
        "policy_id": policy_id,

        "claim_type": None,
        "claimed_amount": None,
        "incident_date": None,
        "extracted_fields": None,

        "coverage_matched": None,
        "coverage_reasoning": None,
        "coverage_exceptions": None,

        "fraud_score": None,
        "fraud_signals": None,

        "decision": None,
        "decision_reasoning": None,

        "audit_trail": [
            {
                "stage": "intake",
                "timestamp": now,
                "note": "Claim created",
            }
        ],
        "current_stage": "intake",
    }