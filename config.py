import os
# 'dotenv' akan diinstal manual oleh pengguna nanti
from dotenv import load_dotenv
from supabase import create_client, Client

# Muat environment variables dari file .env
load_dotenv()

# Konfigurasi Chutes AI
CHUTES_API_URL = "https://llm.chutes.ai/v1/chat/completions"

# Ambil token dari environment variable, berikan pesan error jika tidak ada
CHUTES_API_TOKEN = os.getenv("CHUTES_API_TOKEN")
if not CHUTES_API_TOKEN:
    # Ini akan menghentikan aplikasi jika token tidak ditemukan, yang merupakan perilaku aman.
    raise ValueError("CHUTES_API_TOKEN tidak ditemukan. Harap buat file .env dan tambahkan variabel tersebut.")

MODEL_NAME = "deepseek-ai/DeepSeek-R1"
SAVE_DIR = "chat_logs"

# Konfigurasi Supabase
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
