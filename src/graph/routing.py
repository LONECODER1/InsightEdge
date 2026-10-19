"""
Conditional edge routing for the LangGraph workflow.
"""
from src.graph.state import HedgeFundState


def route_after_risk(state: HedgeFundState) -> str:
    """
    If risk_flag is set, loop back to supervisor for re-evaluation at most once.
    """
    loops = state.get("risk_loops", 0)
    if state.get("risk_flag") and loops < 1:
        return "supervisor"
    return "final_decision"
