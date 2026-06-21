from datetime import datetime, timezone
from typing import Optional

from app.database.database import supabase
from app.state.claim_state import VerisState


def log_audit_event(
    state: VerisState,
    stage: str,
    note: str,
    agent_model: Optional[str] = None,
    result: Optional[dict] = None,
    reasoning: Optional[str] = None,
) -> None:
    """
    Append one audit entry to in-memory state and persist it to the
    append-only audit_log table.

    Call this from every agent node — document review, fraud, coverage,
    decision — instead of writing to state["audit_trail"] or the
    audit_log table directly. Keeps the entry shape consistent across
    every stage of the pipeline.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # in-memory trail, available to the rest of the graph for this run
    state["audit_trail"].append({
        "stage": stage,
        "timestamp": timestamp,
        "note": note,
    })

    # durable, append-only record — survives even if a later node crashes
    try:
        supabase.table("audit_log").insert({
            "claim_id": state["claim_id"],
            "stage": stage,
            "model": agent_model,
            "result": result,
            "reasoning": reasoning,
            "note": note,
        }).execute()
    except Exception as e:
        # deliberately not re-raising — but think about whether a failed
        # audit write should actually halt the node for a pipeline whose
        # entire pitch is auditability. silently continuing here is a
        # judgment call, not a default you should leave unexamined.
        print(f"Failed to write audit_log entry for stage '{stage}': {e}")