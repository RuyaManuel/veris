import httpx
# import os
import base64
import io
from datetime import datetime, timezone
from app.state.claim_state import VerisState
from app.database.database import supabase
from PIL import Image
# from dotenv import load_dotenv


# load_dotenv()

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
        "keep_alive":0
    }

    timeout_config = httpx.Timeout(connect=10.0, read=180.0, write=20.0, pool=10.0)

    with httpx.Client(timeout=timeout_config) as client:
        response = client.post(ollama_url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["response"]

image_analysis_prompt = """
Describe the content of this image.
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
            print("analysis_complete",image_analysis)

        except Exception as e:
             print(f"Doc processing error for {filename}: {e}")