from typing import TypedDict, Literal, Optional
import uuid
from pydantic import BaseModel
from datetime import datetime, timezone


class PipelineError(TypedDict):
    agent: str                  # "coverage", "fraud", "processor", "decision"
    error_type: str             # "timeout", "parse_error", "network_error", "validation_error"
    error_message: str
    attempt_number: int
    timestamp: str
    context: Optional[dict]     # agent-specific detail — doc filename, model used, etc.




class VerisState(TypedDict):
    # Metacontext Data.
    claim_id: str
    claim_type: Optional[str]
    submitted_at: str                          
    policy_id: str
    claimant_id: str
    claim_amount: Optional[float]
    claimant_statement: str
    policy_metadata: Optional[list[dict[str,any]]]
    claimant_history_summary: Optional[dict]

    #Tracking Flags
    is_document_review_done: bool
    is_fraud_analysis_done: bool
    is_coverage_handled: bool
    is_escalated: bool
    is_finalized: bool
    next_agent: Optional[Literal["fraud", "coverage", "finish","escalate","process"]]

    #Evaluation Data.
    document_processing_errors: Optional[list[dict]]
    ai_document_review: Optional[list[dict]]
    extracted_amount: Optional[float]
    incident_date: Optional[str]
    extracted_fields: Optional[dict]
    claim_verdict: Optional[Literal["approved", "denied", "escalated"]]
    claim_verdict_reason: Optional[str]

    # Pipeline Erros
    pipeline_errors: Optional[list[PipelineError]]

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

    # escalation
    escalation_id: str
    escalation_status: str


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