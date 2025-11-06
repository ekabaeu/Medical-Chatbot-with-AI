from flask import Flask, request, jsonify, stream_with_context
from flask_cors import CORS
import requests
import json
import os
import datetime
import re 
import fnmatch # <-- BARU: Import pustaka pencocokan file

# --- Konfigurasi ---
app = Flask(__name__)
CORS(app) 

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "alibayram/medgemma"
SAVE_DIR = "chat_logs"

# === Fungsi Helper untuk Mengamankan CSV ===
def escape_csv(s):
    if not s:
        return '""'
    if ',' in s or '"' in s or '\n' in s:
        return '"' + s.replace('"', '""') + '"'
    return s

# === SYSTEM PROMPT (Ini sudah benar, jangan diubah) ===
system_prompt = {
    "role": "system",
    "content": (
        "Anda adalah Asisten Medis AI yang hening dan efisien. Anda HANYA merespons input pengguna."
        "\n\n"
        "**ATURAN UTAMA: Periksa Panjang Riwayat Chat**"
        "\n\n"
        "**1. JIKA RIWAYAT CHAT PENDEK (1-2 pesan dari 'User'):**"
        "\n"
        "Ini adalah keluhan awal. Tugas Anda adalah memberikan ANALISIS LENGKAP."
        "\n"
        "JANGAN PERNAH menjawab 'Maaf, data tidak lengkap' atau sejenisnya. LANGSUNG ANALISIS apa pun yang diberikan pengguna."
        "\n"
        "GUNAKAN 'Format Analisis Wajib' di bawah ini."
        "\n\n"
        "**2. JIKA RIWAYAT CHAT PANJANG (3+ pesan dari 'User'):**"
        "\n"
        "Ini adalah percakapan lanjutan. TUGAS Anda adalah beralih ke mode PERCAKAPAN NATURAL."
        "\n"
        "ANDA HARUS BERHENTI menggunakan format analisis. Jawablah dengan pertanyaan singkat dan natural."
        "\n"
        "Contoh: 'Terima kasih atas informasinya. Apakah ruamnya juga terasa panas?'"
        "\n\n"
        "--- (AWAL Format Analisis Wajib - HANYA UNTUK CHAT PENDEK) ---"
        "\n"
        "**Analisis Awal:**\n[Analisis Anda berdasarkan keluhan...]\n\n"
        "**Kemungkinan Penyebab:**\n* **[Penyebab 1]:** [Penjelasan...]\n* **[Penyebab 2]:** [Penjelasan...]\n\n"
        "**Pertanyaan Diagnostik Lanjutan:**\n* [Pertanyaan 1?]\n* [Pertanyaan 2?]\n\n"
        "**Rekomendasi Awal:**\n* [Rekomendasi...]"
        "\n"
        "--- (AKHIR Format Analisis Wajib) ---"
        "\n\n"
        "**ATURAN NON-MEDIS:**"
        "\n"
        "Jika pengguna bertanya non-medis (cuaca, film), JAWAB: 'Maaf, saya hanya dapat memproses pertanyaan terkait kesehatan.'"
    )
}

# === Endpoint 1: Untuk Streaming Chat (Ini sudah benar, jangan diubah) ===
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    history_from_frontend = data.get('history', [])
    if not history_from_frontend:
        return jsonify({"error": "Riwayat chat kosong"}), 400
    messages_for_llm = []
    for chat in history_from_frontend:
        role = "user" if chat.get('sender') == 'User' else 'assistant'
        if role == 'assistant' and not chat.get('message'):
            continue
        messages_for_llm.append({"role": role, "content": chat.get('message')})
    final_payload_messages = [system_prompt] + messages_for_llm
    payload = {"model": MODEL_NAME, "messages": final_payload_messages, "stream": True}
    try:
        def generate():
            with requests.post(OLLAMA_API_URL, json=payload, stream=True) as r:
                r.raise_for_status() 
                for line in r.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if "message" in chunk and "content" in chunk["message"]:
                                yield chunk["message"]["content"] 
                        except json.JSONDecodeError: pass 
        return app.response_class(stream_with_context(generate()), mimetype='text/plain')
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        return jsonify({"error": f"Gagal menghubungi Ollama: {e}"}), 500

# === Endpoint 2: Untuk Menyimpan Chat (Overwrite & Rename Otomatis) ===
@app.route('/save-chat', methods=['POST'])
def save_chat():
    """Menerima data, menghapus file sesi lama, dan menyimpan file baru (rename)."""
    
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    try:
        data = request.json
        chat_history = data.get('chatHistory', [])
        session_id = data.get('sessionId')
        patient_data = data.get('patientData', {}) # Ambil data pasien

        if not chat_history or not session_id:
            return jsonify({"error": "Data chat atau sessionId tidak ada"}), 400

        # 1. Tentukan NAMA FILE BARU berdasarkan data pasien saat ini
        name = patient_data.get('name', 'unknown').replace(' ', '_')
        age = patient_data.get('age', 'unknown')
        new_filename = f"chat_{name}_{age}_{session_id}.csv"
        new_filepath = os.path.join(SAVE_DIR, new_filename)

        # 2. Pola untuk MENCARI FILE LAMA
        search_pattern = f"chat_*_*_{session_id}.csv"

        # 3. Cari dan HAPUS file lama
        for f in os.listdir(SAVE_DIR):
            if fnmatch.fnmatch(f, search_pattern):
                # Jika file yang ditemukan BUKAN file baru (artinya ini file lama)
                if f != new_filename:
                    old_filepath = os.path.join(SAVE_DIR, f)
                    os.remove(old_filepath)
                    print(f"File lama {f} dihapus.")
                break # Asumsi hanya ada 1 file per sesi

        # 4. Buat konten CSV
        csv_content = ["Timestamp,Sender,Message\n"]
        for row in chat_history:
            message = row.get('message', '')
            line = f"{row.get('timestamp')},{row.get('sender')},{escape_csv(message)}\n"
            csv_content.append(line)
        csv_string = "".join(csv_content)

        # 5. Tulis (atau Timpa) file dengan NAMA BARU
        with open(new_filepath, 'w', encoding='utf-8') as f:
            f.write(csv_string)
        
        return jsonify({"message": f"Chat disimpan sebagai {new_filename}"}), 200

    except Exception as e:
        print(f"Error saving chat: {e}")
        return jsonify({"error": "Gagal menyimpan chat di server"}), 500

# === Jalankan Server ===
if __name__ == '__main__':
    app.run(debug=True, port=5000)