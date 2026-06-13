from app.state.claim_state import VerisState
from app.database.database import supabase

def run_organiser(state: VerisState):
    response = supabase.table("claims").select("*").limit(1).execute()
    print(f"database response, {response}")

