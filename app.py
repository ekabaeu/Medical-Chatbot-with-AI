from flask import Flask, request, jsonify, stream_with_context
from flask_cors import CORS
import requests
import json
import os
import datetime

# --- Konfigurasi ---
app = Flask(__name__)
CORS(app) 

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma3:270m"
SAVE_DIR = "chat_logs"

# === Fungsi Helper untuk Mengamankan CSV ===
def escape_csv(s):
    """Mengamankan string untuk dimasukkan ke dalam sel CSV."""
    if not s:
        return '""'
    if ',' in s or '"' in s or '\n' in s:
        # Menggunakan perangkaian string biasa agar kompatibel dengan Python lama
        return '"' + s.replace('"', '""') + '"'
    return s

# === Endpoint 1: Untuk Streaming Chat ===
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "Pesan tidak boleh kosong"}), 400

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": user_message}],
        "stream": True
    }

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
                        except json.JSONDecodeError:
                            pass 

        return app.response_class(stream_with_context(generate()), mimetype='text/plain')

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Gagal menghubungi Ollama: {e}"}), 500

# === Endpoint 2: Untuk Menyimpan Chat (MODIFIKASI) ===
@app.route('/save-chat', methods=['POST'])
def save_chat():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    try:
        data = request.json
        patient_data = data.get('patientData', {})
        chat_history = data.get('chatHistory', [])
        
        # --- PERUBAHAN UTAMA: Dapatkan sessionId ---
        session_id = data.get('sessionId')

        if not chat_history or not session_id:
            return jsonify({"error": "Data chat atau sessionId tidak ada"}), 400

        # --- Buat konten CSV ---
        csv_content = [
            f"Nama Pasien,{escape_csv(patient_data.get('name'))}\n",
            f"Umur,{escape_csv(patient_data.get('age'))}\n",
            f"Gender,{escape_csv(patient_data.get('gender'))}\n",
            f"Keluhan Awal,{escape_csv(patient_data.get('complaint'))}\n\n",
            "Timestamp,Sender,Message\n"
        ]
        
        for row in chat_history:
            line = f"{row.get('timestamp')},{row.get('sender')},{escape_csv(row.get('message'))}\n"
            csv_content.append(line)
        
        csv_string = "".join(csv_content)

        # --- PERUBAHAN UTAMA: Nama file berdasarkan sessionId ---
        patient_name = patient_data.get('name', 'unknown').replace(' ', '_')
        # Nama file sekarang konsisten, tidak pakai timestamp
        filename = f"chat_{patient_name}_{session_id}.csv" 
        
        filepath = os.path.join(SAVE_DIR, filename)

        # --- Tulis/Timpa file ke disk server ---
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(csv_string)
        
        # Kirim respons sukses (tidak perlu 'alert' di frontend)
        return jsonify({"message": f"Chat disimpan sebagai {filename}"}), 200

    except Exception as e:
        print(f"Error saving chat: {e}")
        return jsonify({"error": "Gagal menyimpan chat di server"}), 500

# === Jalankan Server ===
if __name__ == '__main__':
    app.run(debug=True, port=5000)