from app.state.claim_state import build_claim_state, BuildParams
from app.graph.claims_graph import app
from app.database.database import supabase


def start_agent(limit: int = 5):
    result = (
        supabase.table("claims")
        .select("*")
        .eq("status", "pending")
        .limit(limit)
        .execute()
    )

    print({"result data": result.data})
    for row in result.data:
        params = BuildParams(
            claim_id=row["id"],
            policy_id=row["policy_id"],
            claimant_id=row["claimant_id"],
            raw_documents=row.get("raw_documents"),
            claimant_statement=row["claimant_statement"],
        )

        state = build_claim_state(params)
    
        try:
            final_state = app.invoke(state)
        except Exception as e:
            print(f"Claim {row['id']} failed: {e}")
            continue


if __name__ == "__main__":
    start_agent(limit=4)