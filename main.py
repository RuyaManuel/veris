from app.state.claim_state import create_claim
from app.graph import app
from app.sample_document.raw_document import raw_documents

initial_state = create_claim(
    raw_documents=[{"type": "invoice", "content": "test"}],
    claimant_id="user-123",
    policy_id="policy-456",
)


initial_state = create_claim(
    raw_documents=raw_documents,
    claimant_id="user-123",
    policy_id="policy-456"
)

result = app.invoke(initial_state)
print(result)