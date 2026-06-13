from app.state.claim_state import create_claim
from app.graph import app


initial_state = create_claim(
    raw_documents=[{"type": "invoice", "content": "test"}],
    claimant_id="user-123",
    policy_id="policy-456",
)

result = app.invoke(initial_state)
print(result)