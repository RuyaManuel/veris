from app.state.claim_state import build_claim_state
from app.graph.claims_graph import app
from app.database.database import supabase
import time


def get_pending_claims(limit: int = 5):
    result = (
        supabase.table("claims")
        .select("*")
        .eq("status", "pending")
        .limit(limit)
        .execute()
    )
    return result.data

claims = get_pending_claims()
print(claims)

# claims_data = {
#     "claim_id": claims.claims_id
# }