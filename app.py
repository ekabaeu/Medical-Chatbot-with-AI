from flask import Flask, request, jsonify, stream_with_context
from flask_cors import CORS
import requests
import json
import os
import datetime
import re 
import fnmatch # Import untuk pencocokan file

# --- Konfigurasi ---
app = Flask(__name__)
CORS(app) 

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "alibayram/medgemma"
SAVE_DIR = "chat_logs"

# === Fungsi Helper untuk Mengamankan CSV ===
def escape_csv(s):
    """Mengamankan string untuk dimasukkan ke dalam sel CSV."""
    if not s:
        return '""'
    if ',' in s or '"' in s or '\n' in s:
        return '"' + s.replace('"', '""') + '"'
    return s

# PROMPT 1: HANYA UNTUK PESAN PERTAMA (Tanya Pertanyaan)
system_prompt_task_1 = {
    "role": "system",
    "content": (
        "Anda adalah Asisten Medis AI. Tugas Anda saat ini adalah MENGUMPULKAN INFORMASI."
        "\n"
        "Pesan terakhir pengguna adalah keluhan awal mereka."
        "\n"
        "ANDA HARUS merespons HANYA dengan 3 pertanyaan diagnostik lanjutan untuk memperjelas keluhan."
        "\n"
        "JAWAB DENGAN FORMAT INI:"
        "\n"
        "Baik, saya telah mencatat keluhan Anda. Untuk memberikan analisis yang lebih akurat, saya perlu beberapa informasi tambahan: "
        "\n"
        "1. [Tulis pertanyaan diagnostik #1 di sini]"
        "\n"
        "2. [Tulis pertanyaan diagnostik #2 di sini]"
        "\n"
        "3. [Tulis pertanyaan diagnostik #3 di sini]"
    )
}

# PROMPT 2: HANYA UNTUK PESAN KEDUA (Beri Analisis)
system_prompt_task_2 = {
    "role": "system",
    "content": (
        "**PERATURAN UTAMA: JANGAN JAWAB PERTANYAAN NON-MEDIS.**"
        "\n"
        "Jika pertanyaan terakhir pengguna JELAS non-medis (matematika, sejarah, politik, cuaca, '1+1', 'siapa kamu'), Anda HARUS DAN HANYA BOLEH menjawab:"
        "\n"
        "'Maaf, saya hanya dapat memproses pertanyaan terkait kesehatan.'"
        "\n"
        "---"
        "\n"
        "**TUGAS ANDA SEKARANG ADALAH MEMBERIKAN ANALISIS LENGKAP.**"
        "\n"
        "Riwayat chat berisi (1) Keluhan Awal dan (2) Jawaban atas 3 pertanyaan Anda."
        "\n"
        "**JANGAN TANYA PERTANYAAN LAGI.**"
        "\n"
        "Anda HARUS menganalisis SEMUA data dan merespons HANYA menggunakan 'Format Analisis Lengkap' di bawah ini."
        "\n\n"
        "Terima kasih atas informasinya. Berikut adalah analisis medis lengkap saya:"
        "\n"
        "**Analisis Medis:**\n[Analisis Anda berdasarkan keluhan DAN jawaban...]\n\n"
        "**Kemungkinan Penyebab:**\n* **[Penyebab 1]:** [Penjelasan...]\n* **[Penyebab 2]:** [Penjelasan...]\n\n"
        "**Rekomendasi:**\n* [Rekomendasi jelas...]"
    )
}

# PROMPT 3: UNTUK PESAN KETIGA DAN SETERUSNYA (Natural)
system_prompt_task_3 = {
    "role": "system",
    "content": (
        "**PERATURAN UTAMA: JANGAN JAWAB PERTANYAAN NON-MEDIS.**"
        "\n"
        "Jika pertanyaan terakhir pengguna JELAS non-medis (matematika, sejarah, politik, cuaca, '1+1', 'siapa kamu'), Anda HARUS DAN HANYA BOLEH menjawab:"
        "\n"
        "'Maaf, saya hanya dapat memproses pertanyaan terkait kesehatan.'"
        "\n"
        "---"
        "\n"
        "**TUGAS ANDA SEKARANG ADALAH PERCAKAPAN NATURAL.**"
        "\n"
        "Anda telah memberikan analisis lengkap."
        "\n"
        "**JANGAN PERNAH** menggunakan format analisis lagi. Jawab pertanyaan lanjutan pengguna (yang terkait medis) dengan singkat dan natural."
    )
}


# === Endpoint 1: Untuk Streaming Chat ===
@app.route('/chat', methods=['POST'])
def chat():
    """Menangani permintaan chat dari frontend."""
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
    

    # === PERBAIKAN: FILTER NON-MEDIS DI SINI ===
    if messages_for_llm and messages_for_llm[-1]['role'] == 'user':
        last_user_message = messages_for_llm[-1]['content'].lower()
        
        # Daftar kata kunci sederhana
        non_medical_keywords = [
            '1+1', 'cuaca', 'sejarah', 'presiden', 'politik', 
            'siapa kamu', 'matematika', 'fisika'
        ]
        
        # Pola regex untuk mendeteksi operasi matematika sederhana
        math_pattern = re.compile(r'berapa\s*\d+\s*[+\-*/xX]\s*\d+')

        is_non_medical = False
        for keyword in non_medical_keywords:
            if keyword in last_user_message:
                is_non_medical = True
                break
        
        if not is_non_medical and math_pattern.search(last_user_message):
            is_non_medical = True

        if is_non_medical:
            # Jangan panggil Ollama. Langsung kirim respons penolakan.
            # Kita harus mengembalikannya sebagai stream agar frontend menanganinya dengan benar.
            def generate_refusal():
                yield "Maaf, saya hanya dapat memproses pertanyaan terkait kesehatan."
            
            return app.response_class(stream_with_context(generate_refusal()), mimetype='text/plain')
    # ============================================


    # Hitung jumlah pesan 'user' untuk logika prompt
    user_message_count = sum(1 for msg in messages_for_llm if msg['role'] == 'user')
    
    # === LOGIKA 3 TAHAP BARU ===
    if user_message_count == 1:
        final_system_prompt = system_prompt_task_1
    elif user_message_count == 2:
        final_system_prompt = system_prompt_task_2
    else:
        final_system_prompt = system_prompt_task_3
    # ============================
    
    final_payload_messages = [final_system_prompt] + messages_for_llm

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
        patient_data = data.get('patientData', {}) 

        if not chat_history or not session_id:
            return jsonify({"error": "Data chat atau sessionId tidak ada"}), 400

        name = patient_data.get('name', 'unknown').replace(' ', '_')
        age = patient_data.get('age', 'unknown')
        new_filename = f"chat_{name}_{age}_{session_id}.csv"
        new_filepath = os.path.join(SAVE_DIR, new_filename)

        search_pattern = f"chat_*_*_{session_id}.csv"

        for f in os.listdir(SAVE_DIR):
            if fnmatch.fnmatch(f, search_pattern):
                if f != new_filename:
                    old_filepath = os.path.join(SAVE_DIR, f)
                    try:
                        os.remove(old_filepath)
                        print(f"File lama {f} dihapus.")
                    except OSError as e:
                        print(f"Error menghapus file lama {f}: {e}")
                break 

        csv_content = ["Timestamp,Sender,Message\n"]
        for row in chat_history:
            message = row.get('message', '')
            line = f"{row.get('timestamp')},{row.get('sender')},{escape_csv(message)}\n"
            csv_content.append(line)
        csv_string = "".join(csv_content)

        with open(new_filepath, 'w', encoding='utf-8') as f:
            f.write(csv_string)
        
        return jsonify({"message": f"Chat disimpan sebagai {new_filename}"}), 200

    except Exception as e:
        print(f"Error saving chat: {e}")
        return jsonify({"error": "Gagal menyimpan chat di server"}), 500

# === Jalankan Server ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)