import httpx
import os
import base64
import io
from datetime import datetime, timezone
from app.state.claim_state import VerisState
from app.database.database import supabase
import moondream as md
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
model = md.vl(api_key=os.getenv("MOONDREAM_KEY"))

def fetch_document_bytes(url: str) -> bytes:
    with httpx.Client(timeout=30) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content

# def analyze_with_moondream(param:str, prompt: str) -> str:
#         # for now we use an external api just so we get the automation right.
#         raw_bytes = fetch_document_bytes(param)
#         image = Image.open(io.BytesIO(raw_bytes))
#         image = image.convert("RGB")
#         result = model.query(image, prompt)
#         return result["answer"]

def analyze_with_moondream(url: str, prompt: str) -> str:
    raw_bytes = fetch_document_bytes(url)
    image = Image.open(io.BytesIO(raw_bytes))
    image = image.convert("RGB")
    
    # save to fresh buffer to ensure clean image data
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    clean_image = Image.open(buffer)
    
    result = model.query(clean_image, prompt)
    return result["answer"]

image_analysis_prompt = """
You are an AI claims assessor for a solar installation insurance system. Analyze the submitted image and return a structured assessment covering two areas:
## 1. DOCUMENT VALIDITY
- Document type detected (invoice, installation certificate, warranty, site survey, photo evidence, other)
- Visual consistency: fonts, alignment, spacing, logo placement — flag irregularities
- Signs of digital manipulation: clean edges, mismatched backgrounds, artifacting, inconsistent lighting or shadows
- Signs of AI generation: overly perfect layout, generic content, unnatural uniformity
- Authenticity signal: GENUINE / SUSPICIOUS / LIKELY FABRICATED — with brief reasoning
- Confidence: HIGH / MEDIUM / LOW

## 2. DAMAGE ASSESSMENT
- Visible components: panels, inverter, mounting hardware, wiring, roof interface
- Damage type per affected component: physical impact, burn marks, corrosion, delamination, cracking, water ingress
- Severity per component: MINOR / MODERATE / SEVERE / TOTAL LOSS
- Consistency signal: does visible damage match a plausible incident — CONSISTENT / INCONSISTENT / UNCLEAR
- Overall claim validity signal with reasoning

## 3. FLAGS FOR HUMAN REVIEW
List any observations across either section that require a human adjudicator. If none, state "No flags raised."
---
Be specific and evidence-based. If a component or document element is not visible or not assessable from this image, state that explicitly rather than inferring. This assessment is a preliminary automated screen — final decisions are made by a licensed human adjudicator.
"""


def process_docs(state: VerisState) -> VerisState:
    claim_id = state["claim_id"]

    result = (
        supabase.table("documents")
        .select("*")
        .eq("claim_id", claim_id)
        .execute()
    )

    docs = result.data or []
    document_analysis = []

    for doc in docs:
        url = doc.get("file_url")
        filename = doc.get("filename", "")

        if not url:
            continue

        try:
            # raw_bytes = fetch_document_bytes(url) : would make this functional when models are installed and run locally.

            if filename.lower().endswith(".pdf"):
                document_type = "application/pdf"
            elif filename.lower().endswith((".jpg", ".jpeg")):
                document_type = "image/jpeg"
            elif filename.lower().endswith(".png"):
                document_type = "image/png"
            else:
                document_type = "application/octet-stream"

            # process doc with moondream ai

            image_analysis = analyze_with_moondream(url,image_analysis_prompt)
            print({"analysis_complete",image_analysis})

        except Exception as e:
             print(f"Doc processing error for {filename}: {e}")