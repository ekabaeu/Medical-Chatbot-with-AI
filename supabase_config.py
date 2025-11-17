import os
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.
    This function safely handles client creation with environment variables.
    """
    try:
        # Get Supabase credentials from environment variables
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        # Check if required environment variables are set
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        return supabase
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        raise e
