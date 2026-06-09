from langgraph.graph import StateGraph, START, END
from app.state.claim_state import ClaimState
from app.agents.organiser import run_organiser

graph = StateGraph(ClaimState)

graph.add_node("organiser", run_organiser)
graph.add_edge(START, "organiser")

