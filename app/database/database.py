import os
from supabase import Client, create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE_KEY= os.getenv("SERVICE_ROLE_KEY")

if not SERVICE_ROLE_KEY or not SUPABASE_URL:
    raise ValueError("Missing Database credentials!")

supabase: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY )