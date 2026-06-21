import httpx
import base64
import io
from datetime import datetime, timezone
from app.state.claim_state import VerisState
from app.database.database import supabase
from app.database.audit import log_audit_event
from PIL import Image


def fetch_document_bytes(url: str) -> bytes:
    with httpx.Client(timeout=30) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


def analyze_with_moondream(url: str, prompt: str) -> str:
    raw_bytes = fetch_document_bytes(url)
    image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    # save to fresh buffer to ensure clean image data
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    jpeg_bytes = buffer.getvalue()
    base64_image = base64.b64encode(jpeg_bytes).decode("utf-8")
    ollama_url = "http://localhost:11434/api/generate"

    payload = {
        "model": "moondream:v2",
        "prompt": prompt,
        "images": [base64_image],
        "stream": False,  # Crucial: This returns a single JSON object instead of a stream
        "keep_alive": 0,
    }

    timeout_config = httpx.Timeout(connect=10.0, read=180.0, write=20.0, pool=10.0)

    with httpx.Client(timeout=timeout_config) as client:
        response = client.post(ollama_url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["response"]


# Moondream prompt.
image_analysis_prompt = """
Describe the content of this image.
"""


def get_document_type(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "application/pdf"
    if lower.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if lower.endswith(".png"):
        return "image/png"
    return "application/octet-stream"


def process_docs(state: VerisState) -> VerisState:
    claim_id = state["claim_id"]

    result = (
        supabase.table("documents")
        .select("*")
        .eq("claim_id", claim_id)
        .execute()
    )
    docs = result.data or []

    # ai_document_review is typed as list[dict] on VerisState, not a dict —
    # use a dict internally keyed by document_id for O(1) dedup on re-entry,
    # then flatten back to a list before writing to state
    existing_reviews = state.get("ai_document_review") or []
    reviews_by_doc_id = {
        r["document_id"]: r for r in existing_reviews if r.get("document_id")
    }

    succeeded = 0
    failed = 0

    for doc in docs:
        url = doc.get("file_url")
        filename = doc.get("filename", "")
        doc_id = doc.get("id")

        if not url or not doc_id:
            continue

        document_type = get_document_type(filename)
        processed_at = datetime.now(timezone.utc).isoformat()

        try:
            image_analysis = analyze_with_moondream(url, image_analysis_prompt)
            print("analysis_complete", filename)

            reviews_by_doc_id[doc_id] = {
                "document_id": doc_id,
                "filename": filename,
                "document_type": document_type,
                "analysis": image_analysis,
                "model": "moondream:v2",
                "status": "completed",
                "processed_at": processed_at,
            }
            succeeded += 1

            # write the observation back to its own document record —
            # process_docs owns this write, the decision node does not
            supabase.table("documents").update({
                "extracted_content": image_analysis,
                "extraction_model": "moondream:v2",
                "processed_at": processed_at,
                "status": "completed",
            }).eq("id", doc_id).execute()

        except Exception as e:
            error_message = str(e)
            print(f"Doc processing error for {filename}: {error_message}")
            failed += 1

            reviews_by_doc_id[doc_id] = {
                "document_id": doc_id,
                "filename": filename,
                "document_type": document_type,
                "status": "failed",
                "error": error_message,
                "processed_at": processed_at,
            }

            try:
                supabase.table("documents").update({
                    "status": "failed",
                    "error": error_message,
                    "processed_at": processed_at,
                }).eq("id", doc_id).execute()
            except Exception as db_error:
                # don't let a logging failure mask the original processing error
                print(f"Failed to record error state for {filename}: {db_error}")

    state["ai_document_review"] = list(reviews_by_doc_id.values())

    log_audit_event(
        state,
        stage="document_review",
        note=f"Processed {len(docs)} document(s): {succeeded} succeeded, {failed} failed",
        agent_model="moondream:v2",
        result={
            "documents_processed": len(docs),
            "succeeded": succeeded,
            "failed": failed,
        },
    )
    state["current_stage"] = "document_review"

    return state