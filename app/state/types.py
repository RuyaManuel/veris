from typing import TypedDict, Optional, Literal

class FraudSignalDetail(TypedDict):
    signal: str           # "date_inconsistency"
    description: str      # "Claim form states 15th Jan, police report states 18th Jan"
    severity: Literal["critical", "warning", "info"]


class PipelineError(TypedDict):
    agent: str                  # "coverage", "fraud", "processor", "decision"
    error_type: str             # "timeout", "parse_error", "network_error", "validation_error"
    error_message: str
    attempt_number: int
    timestamp: str
    context: Optional[dict]   

class AuditEvent(TypedDict):
    stage: str
    timestamp: str
    note: str
    agent_model: Optional[str]
    result: Optional[dict]
    reasoning: Optional[str] 

class EscalationRecord(TypedDict):
    escalation_id: Optional[str]
    escalation_status: Optional[Literal["pending_review", "under_review", "resolved"]]
    escalation_trigger: Optional[str]
    escalation_severity: Optional[Literal["critical", "warning"]]
    escalation_metadata: Optional[EscalationMetadata]


class FraudEvaluation(TypedDict):
    fraud_score: float
    fraud_threshold_used: float
    fraud_signals: list[str]
    fraud_signal_details: Optional[FraudSignalDetail]  # [{signal, description, severity}]
    amount_discrepancy: Optional[float]
    date_discrepancy_days: Optional[int]
    model_used: str
    evaluated_at: str

class CoverageEvaluation(TypedDict):
    # Core determination
    is_coverage_matched: Optional[bool]
    coverage_reasoning: Optional[str]
    coverage_exceptions: Optional[list[dict]]

    # Peril
    is_peril_matched: Optional[bool]
    matched_peril: Optional[str]                # "collision", "theft", "fire"

    # Period
    is_policy_period_valid: Optional[bool]

    # Financial
    applicable_coverage_limit: Optional[float]
    applicable_deductible: Optional[float]
    estimated_payout_amount: Optional[float]
    is_partial_coverage: Optional[bool]
    estimated_remaining_limit: Optional[float]

    # Policy standing
    policy_status_at_incident: Optional[Literal["active", "lapsed", "cancelled", "suspended"]]
    is_premiums_current: Optional[bool]

    # Geography
    is_incident_location_covered: Optional[bool]

    # Model metadata
    model_used: str
    evaluated_at: str