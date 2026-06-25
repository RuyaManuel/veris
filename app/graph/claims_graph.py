from langgraph.graph import StateGraph, START, END
from app.state.claim_state import VerisState
from app.agents.processor import process_docs
from app.agents.decision import route_decision
from app.agents.fraud import fraud_scan
from app.agents.coverage import _coverage
from app.database.audit import run_audit
from app.agents.escalation import run_escalation

graph = StateGraph(VerisState)

# node setup
graph.add_node("processor", process_docs)
graph.add_node("decision",route_decision)
graph.add_node("fraud", fraud_scan)
graph.add_node("coverage", _coverage)
graph.add_node('audit', run_audit)
graph.add_node('escalate',run_escalation)

# Edge setup
# routing function defined here:
def route_choice(state: VerisState):
    next_agent = state.get("next_agent")
    if not next_agent:
        raise ValueError(f"decision node did not set next_agent. State: {state}")
    return next_agent

graph.add_edge(START, "processor")
graph.add_edge("processor","decision")
graph.add_conditional_edges("decision", route_choice, {
    "fraud": "fraud",
    "coverage": "coverage",
    "finish": "audit",
    "escalate": 'escalate',
    "process": 'processor'
})
graph.add_edge("fraud","decision")
graph.add_edge('coverage',"decision")
graph.add_edge("escalate","audit")
graph.add_edge('audit', END)


app = graph.compile()
