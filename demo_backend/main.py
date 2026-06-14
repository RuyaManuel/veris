from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime, timezone, date
import uuid
from db import supabase

app = FastAPI()

class RegisterClient(BaseModel):
    company_name: str
    registration_number: str
    risk_profile: Optional[dict]

class CreatePolicy(BaseModel):
    policy_number: str
    client_id: str
    status: str
    underwriter: str
    effective_date: datetime
    expiration_date: datetime
    pdf_local_path: str
    coverage_matrix: list[dict]
    automation_rules: list[dict]

class ClaimRequest(BaseModel):
    policy_id: str
    claimant_id: str
    claimant_statement: Optional[str] = None
    claim_type: Optional[str] = None
    claimed_amount: Optional[float] = None
    incident_date: Optional[date] = None
    raw_documents: Optional[list[dict[str, Any]]] = None

class PolicyMetadataRequest(BaseModel):
    policy_id: str
    coverage_sections: Optional[list[dict[str, Any]]] = None
    claims_matrix: Optional[list[dict[str, Any]]] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    source_document_hash: Optional[str] = None
    extraction_model: Optional[str] = None

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


@app.post('/createPolicy')
def create_policy(request: CreatePolicy):
    now = datetime.now(timezone.utc).isoformat()
    policy_id = str(uuid.uuid4())
    row = {
        "id": policy_id,
        "policy_number": request.policy_number,
        "client_id": request.client_id,
        "status": request.status,
        "underwriter": request.underwriter,
        "effective_date": request.effective_date.isoformat(),
        "expiration_date": request.expiration_date.isoformat(),
        "pdf_local_path": request.pdf_local_path,
        "coverage_matrix": request.coverage_matrix,
        "automation_rules": request.automation_rules,
        "created_at": now,
        "updated_at": now,
    }

    try:
        results = supabase.table("policies").insert(row).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not results.data:
        raise HTTPException(status_code=500, detail="Failed to create Policy")
    
    return {"policy_id": policy_id, "status": "created"}


@app.post('/claims')
def create_claim_endpoint(request: ClaimRequest):
    now = datetime.now(timezone.utc).isoformat()
    claim_id = str(uuid.uuid4())

    row = {
        "id": claim_id,
        "policy_id": request.policy_id,
        "claimant_id": request.claimant_id,
        "submitted_at": now,
        "created_at": now,
        "updated_at": now,
        "claim_type": request.claim_type,
        "claimed_amount": request.claimed_amount,
        "incident_date": request.incident_date.isoformat() if request.incident_date else None,
        "processed_documents": [],  # NOT NULL, default empty until document worker populates
        "claimant_statement": request.claimant_statement,
        "raw_documents": request.raw_documents,
    }

    try:
        results = supabase.table('claims').insert(row).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not results.data:
        raise HTTPException(status_code=500, detail="Failed to create claim")

    return {"claim_id": claim_id, "status": "created"}

@app.post('/policy_metadata')
def create_policy_metadata(request: PolicyMetadataRequest):
    now = datetime.now(timezone.utc).isoformat()
    metadata_id = str(uuid.uuid4())

    row = {
        "id": metadata_id,
        "policy_id": request.policy_id,
        "coverage_sections": request.coverage_sections,
        "claims_matrix": request.claims_matrix,
        "effective_date": request.effective_date.isoformat() if request.effective_date else None,
        "expiry_date": request.expiry_date.isoformat() if request.expiry_date else None,
        "extracted_at": now,
        "source_document_hash": request.source_document_hash,
        "extraction_model": request.extraction_model,
    }

    try:
        results = supabase.table('policy_metadata').insert(row).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not results.data:
        raise HTTPException(status_code=500, detail="Failed to create policy metadata")

    return {"metadata_id": metadata_id, "status": "created"}