import os
# 'dotenv' akan diinstal manual oleh pengguna nanti
from dotenv import load_dotenv

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
