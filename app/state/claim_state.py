from typing import TypedDict, Literal, Optional
import uuid
from pydantic import BaseModel
from datetime import datetime, timezone
from app.state.types import PipelineError, FraudEvaluation, CoverageEvaluation, AuditEvent, EscalationRecord


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
    proccess_attempt: int

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
    fraud_evaluation: Optional[FraudEvaluation]
    pipeline_errors: Optional[list[PipelineError]]
    coverage_evaluation: Optional[CoverageEvaluation]

    # Audit
    audit_trail: list[AuditEvent]                    # append-only, never overwrite
    current_stage: Literal[
    "intake",
    "processor",
    "fraud_analysis",
    "coverage_evaluation",
    "routing",
    "final_decision",
    "escalated",
    "completed",
]

    # escalation
    escalation: Optional[EscalationRecord]


class BuildParams(BaseModel):
    claimant_id: str
    policy_id: str
    claim_id: str
    claimant_statement: str


def build_claim_state(params: BuildParams) -> VerisState:
    now = datetime.now(timezone.utc).isoformat()
    return {
        # ── Metacontext ──
        "claim_id": params.claim_id,
        "submitted_at": now,
        "claimant_id": params.claimant_id,
        "policy_id": params.policy_id,
        "claimant_statement": params.claimant_statement,
        "claim_amount": None,
        "claim_type": None,
        "process_attempt": 0,
        "policy_metadata": None,
        "claimant_history_summary": None,

        # ── Tracking Flags ───
        "is_document_review_done": False,
        "is_fraud_analysis_done": False,
        "is_coverage_handled": False,
        "is_escalated": False,
        "is_finalized": False,
        "next_agent": None,

        # ── Evaluation Data ───
        "ai_document_review": None,
        "extracted_amount": None,
        "incident_date": None,
        "extracted_fields": None,
        "fraud_evaluation": None,
        "coverage_evaluation": None,

        # ── Escalation ───
        "escalation": None,

        # ── Pipeline Errors ──
        "pipeline_errors": None,

        # ── Audit ──
        "audit_trail": [
            {
                "stage": "intake",
                "timestamp": now,
                "note": "Claim created",
                "agent_model": None,
                "result": None,
                "reasoning": None,
            }
        ],
        "current_stage": "intake",
    }