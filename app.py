from flask import Flask, request, jsonify, stream_with_context
from flask_cors import CORS
import requests
import json
import os
import fnmatch

# Impor dari file-file baru
import config
from prompts import system_prompt_task_1, system_prompt_task_2, system_prompt_task_3
from utils import escape_csv

# --- Konfigurasi Aplikasi ---
app = Flask(__name__)
CORS(app) 

def stream_chutes_ai_response(payload):
    """Menangani koneksi dan streaming dari Chutes AI API."""
    headers = {
        "Authorization": f"Bearer {config.CHUTES_API_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        with requests.post(config.CHUTES_API_URL, headers=headers, json=payload, stream=True, timeout=180) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith("data:"):
                        data_str = line_str[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            # Ekstrak konten dari chunk sesuai struktur API
                            if chunk.get("choices") and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON chunk: {data_str}")
                            pass
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Chutes AI: {e}")
        yield f"Error: Gagal terhubung ke layanan AI. {e}"


# === Endpoint 1: Untuk Streaming Chat ===
@app.route('/chat', methods=['POST'])
def chat():
    """Menangani permintaan chat dari frontend menggunakan Chutes AI."""
    data = request.json
    history_from_frontend = data.get('history', [])
    if not history_from_frontend:
        return jsonify({"error": "Riwayat chat kosong"}), 400

    # Ubah format history untuk Chutes AI
    messages_for_llm = []
    for chat_item in history_from_frontend:
        role = "user" if chat_item.get('sender') == 'User' else 'assistant'
        content = chat_item.get('message')
        if content:
            messages_for_llm.append({"role": role, "content": content})

    # Filter pertanyaan non-medis
    if messages_for_llm and messages_for_llm[-1]['role'] == 'user':
        last_user_message = messages_for_llm[-1]['content'].lower()
        non_medical_keywords = [
            '1+1', 'cuaca', 'sejarah', 'presiden', 'politik', 
            'siapa kamu', 'matematika', 'fisika', 'berapa'
        ]
        if any(keyword in last_user_message for keyword in non_medical_keywords):
            def generate_refusal():
                yield "Maaf, saya hanya dapat memproses pertanyaan terkait kesehatan."
            return app.response_class(stream_with_context(generate_refusal()), mimetype='text/plain')

    # === LOGIKA 3 TAHAP BARU ===
    user_message_count = sum(1 for msg in messages_for_llm if msg['role'] == 'user')
    
    if user_message_count == 1:
        final_system_prompt = system_prompt_task_1
    elif user_message_count == 2:
        final_system_prompt = system_prompt_task_2
    else:
        final_system_prompt = system_prompt_task_3
    # ============================

    # Siapkan payload untuk Chutes AI
    final_payload_messages = [final_system_prompt] + messages_for_llm
    
    payload = {
        "model": config.MODEL_NAME,
        "messages": final_payload_messages,
        "stream": True,
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    return app.response_class(stream_with_context(stream_chutes_ai_response(payload)), mimetype='text/plain')


# === Endpoint 2: Untuk Menyimpan Chat (Overwrite & Rename Otomatis) ===
@app.route('/save-chat', methods=['POST'])
def save_chat():
    """Menerima data, menghapus file sesi lama, dan menyimpan file baru (rename)."""
    
    if not os.path.exists(config.SAVE_DIR):
        os.makedirs(config.SAVE_DIR)

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
        new_filepath = os.path.join(config.SAVE_DIR, new_filename)

        search_pattern = f"chat_*_*_{session_id}.csv"

        for f in os.listdir(config.SAVE_DIR):
            if fnmatch.fnmatch(f, search_pattern):
                if f != new_filename:
                    old_filepath = os.path.join(config.SAVE_DIR, f)
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