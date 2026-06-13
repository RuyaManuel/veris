from langgraph.graph import StateGraph, START, END
from app.state.claim_state import VerisState
from app.agents.organiser import run_organiser
from app.agents.decision import make_decision
from app.agents.fraud import fraud_scan
from app.agents.coverage import _coverage
from app.agents.audit import run_audit
from app.agents.escalation import run_escalation

graph = StateGraph(VerisState)

# node setup
graph.add_node("organiser", run_organiser)
graph.add_node("decision",make_decision)
graph.add_node("fraud", fraud_scan)
graph.add_node("coverage", _coverage)
graph.add_node('audit', run_audit)
graph.add_node('escalate',run_escalation)

# Edge setup
# routing function defined here:
def route_choice(state: VerisState):
    return state["next_agent"]

graph.add_edge(START, "organiser")
graph.add_edge("organiser","decision")
graph.add_conditional_edges("decision", route_choice, {
    "fraud_analysis": "fraud",
    "coverage_analysis": "coverage",
    "finish": "audit",
    "escalate": 'escalate'
})
graph.add_edge("fraud","decision")
graph.add_edge('coverage',"decision")
graph.add_edge("escalate","audit")
graph.add_edge('audit', END)


app = graph.compile()
