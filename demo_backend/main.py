from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
from db import supabase

app = FastAPI()


class ClaimRequest(BaseModel):
    claimant_id: str
    policy_id: str
    claimant_statement: str

class RegisterClient(BaseModel):
    company_name: str
    registration_number: str
    risk_profile: Optional[dict]



@app.post('/claims')
def create_claim_endpoint(request: ClaimRequest):
    now = datetime.now(timezone.utc).isoformat()
    claim_id = str(uuid.uuid4())

    row = {
        "id": claim_id,
        "submitted_at": now,
        "policy_id": request.policy_id,
        "claimant_id": request.claimant_id,
        "claimant_statement": request.claimant_statement,
        "current_stage": "intake",
        "audit_trail": [
            {"stage": "intake", "timestamp": now, "note": "Claim created"}
        ],
    }

    results = supabase.table('claims').insert(row).execute()

    if not results.data:
        raise HTTPException(status_code=500, detail="Failed to create claim")
    
    return {"claim_id": claim_id, "status": "intake"}


@app.post('/register')
def register_client(request: RegisterClient):
    print("This works!")
    now = datetime.now(timezone.utc).isoformat()
    client_id = str(uuid.uuid4())

    row = {
        "id": client_id,
        "company_name": request.company_name,
        "registration_number": request.registration_number,
        "risk_profile": request.risk_profile,
    }

    try:
        results = supabase.table('clients').insert(row).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not results.data:
        raise HTTPException(status_code=500,detail="Failed to register client")

    return {"client_id": client_id, "status": "Request sucessful"}
