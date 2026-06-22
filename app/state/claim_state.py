from typing import TypedDict, Literal, Optional
import uuid
from pydantic import BaseModel
from datetime import datetime, timezone


class VerisState(TypedDict):
    # Claim identity
    claim_id: str
    claim_type: Optional[str]
    submitted_at: str                          # ISO string — safe to serialize
    policy_id: str
    claimant_id: str
    claimant_statement: str
    process_attempt: int

    #After document / claim processing.
    ai_document_review: Optional[list[dict]]
    claimed_amount: Optional[float]
    incident_date: Optional[str]
    extracted_fields: Optional[dict]
    policy_metadata: Optional[list[dict[str,any]]]

    # Decision State
    next_agent: Optional[Literal["fraud", "coverage", "finish","escalate","process"]]
    decision: Optional[Literal["approved", "denied", "escalated"]]
    decision_reasoning: Optional[str]

    # Coverage State
    coverage_matched: Optional[bool]
    coverage_reasoning: Optional[str]
    coverage_exceptions: Optional[list[dict]]
    # Fraud State
    fraud_score: Optional[float]
    fraud_signals: Optional[list[str]]
    # Audit
    audit_trail: list[dict]                    # append-only, never overwrite
    current_stage: str


class BuildParams(BaseModel):
    claimant_id: str
    policy_id: str
    claim_id: str
    claimant_statement: str


def build_claim_state(params: BuildParams) -> VerisState:
    now = datetime.now(timezone.utc).isoformat()
    return {
        # initial intake
        "claim_id": params.claim_id,
        "submitted_at": now,
        "claimant_id" : params.claimant_id,
        "policy_id": params.policy_id,
        "claimant_statement": params.claimant_statement,
        
        # Processed information
        "policy_metadata": None,
        "process_attempt": None,
        "ai_document_review": None,
        "claim_type": None,
        "claimed_amount": None,
        "incident_date": None,
        "extracted_fields": None,
        "next_agent": None,
        "coverage_matched": None,
        "coverage_reasoning": None,
        "coverage_exceptions": None,

        #fraud related information
        "fraud_score": None,
        "fraud_signals": None,
        
        # Decision related information
        "decision": None,
        "decision_reasoning": None,

        # final state: audit trail
        "audit_trail": [
            {
                "stage": "intake",
                "timestamp": now,
                "note": "Claim created",
            }
        ],
        "current_stage": "intake",
    }