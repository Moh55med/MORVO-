from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

supabase = create_client(url, key)

def test_supabase_connection():
    """Test function to verify Supabase connection"""
    try:
        # Try to select from mentions table
        response = supabase.table("mentions").select("*").limit(1).execute()
        print("Select test successful:", response)
        return {"success": True, "data": response.data}
    except Exception as e:
        print("Supabase error:", str(e))
        return {"success": False, "error": str(e)}