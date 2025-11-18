from flask import Flask, request, jsonify, stream_with_context, Response
from flask_cors import CORS
import requests
import json
import os
import fnmatch
import uuid

# Impor dari file-file proyek
import config
from prompts import system_prompt_task_1, system_prompt_task_2, system_prompt_task_3
import utils  # Impor seluruh modul utils

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
                            if chunk.get("choices") and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON chunk: {data_str}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Chutes AI: {e}")
        yield f"Error: Gagal terhubung ke layanan AI. {e}"


def handle_patient_data_request(message):
    """Handle patient data requests and return formatted response."""
    # Ekstrak ID pasien dari pesan
    patient_id = message.split(' ', 1)[1].strip()
    print(f"ID pasien yang diekstrak: '{patient_id}'")

    # Cari data pasien di database
    patient_data = utils.get_patient_data_by_id(patient_id)
    
    if patient_data:
        # Format data pasien untuk ditampilkan
        response_text = (
            "Data Pasien:\n"
            f"- ID Pasien: {patient_data['id_pasien']}\n"
            f"- Nama: {patient_data['nama']}\n"
            f"- Umur: {patient_data['umur']} tahun\n"
            f"- Gender: {patient_data['gender']}\n"
            f"- Keluhan Awal: {patient_data['keluhan_awal']}"
        )
    else:
        response_text = f"Data pasien dengan ID {patient_id} tidak ditemukan."
    
    # Kembalikan respons langsung tanpa menghubungi AI
    def generate_patient_data_response():
        yield response_text
    return Response(stream_with_context(generate_patient_data_response()), mimetype='text/plain')

# === Endpoint 1: Untuk Streaming Chat ===
@app.route('/chat', methods=['POST'])
def chat():
    """Menangani permintaan chat dari frontend dan menyimpan data pasien pada pesan pertama."""
    data = request.json
    history_from_frontend = data.get('history', [])
    session_id = data.get('sessionId', str(uuid.uuid4()))  # Generate session ID if not provided
    if not history_from_frontend:
        return jsonify({"error": "Riwayat chat kosong"}), 400

    messages_for_llm = []
    for chat_item in history_from_frontend:
        role = "user" if chat_item.get('sender') == 'User' else 'assistant'
        content = chat_item.get('message')
        if content:
            messages_for_llm.append({"role": role, "content": content})

    if messages_for_llm and messages_for_llm[-1]['role'] == 'user':
        last_user_message = messages_for_llm[-1]['content']
        last_user_message_lower = last_user_message.lower()
        
        # Cek apakah pesan adalah permintaan untuk melihat data pasien
        if last_user_message_lower.startswith('cek ') and sum(1 for msg in messages_for_llm if msg['role'] == 'user') == 1:
            return handle_patient_data_request(last_user_message)
        
        # Untuk pengecekan kata kunci non-medis
        non_medical_keywords = [
            '1+1', 'cuaca', 'sejarah', 'presiden', 'politik',
            'siapa kamu', 'matematika', 'fisika', 'berapa'
        ]
        if any(keyword in last_user_message_lower for keyword in non_medical_keywords):
            def generate_refusal():
                yield "Maaf, saya hanya dapat memproses pertanyaan terkait kesehatan."
            return Response(stream_with_context(generate_refusal()), mimetype='text/plain')

    user_message_count = sum(1 for msg in messages_for_llm if msg['role'] == 'user')
    
    patient_info = {}
    final_system_prompt = system_prompt_task_1
    
    # === LOGIKA PENYIMPANAN DATA PASIEN PADA PESAN PERTAMA ===
    if user_message_count == 1:
        initial_complaint = messages_for_llm[-1]['content']
         
        # Ekstrak info dari pesan
        patient_info = utils.extract_patient_info(initial_complaint)
         
        # Buat ID Pasien
        patient_id = utils.generate_patient_id()
         
        # Simpan ke Supabase (primary storage)
        utils.save_patient_data_supabase(
            patient_id=patient_id,
            name=patient_info['nama'],
            age=patient_info['umur'],
            gender=patient_info['gender'],
            initial_complaint=patient_info['keluhan_awal'],
            session_id=session_id
        )
        final_system_prompt = system_prompt_task_1
    # ==========================================================
    elif user_message_count == 2:
        final_system_prompt = system_prompt_task_2
    else:
        final_system_prompt = system_prompt_task_3

    final_payload_messages = [final_system_prompt] + messages_for_llm
    
    payload = {
        "model": config.MODEL_NAME,
        "messages": final_payload_messages,
        "stream": True,
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    response = Response(stream_with_context(stream_chutes_ai_response(payload)), mimetype='text/plain')
    response.headers['X-Session-ID'] = session_id
    response.headers['Access-Control-Expose-Headers'] = 'X-Patient-Data, X-Session-ID'

    if patient_info:
        response.headers['X-Patient-Data'] = json.dumps(patient_info)

    return response


# === Endpoint 2: Untuk Menyimpan Chat (Overwrite & Rename Otomatis) ===
@app.route('/save-chat', methods=['POST'])
def save_chat():
    """Menerima data dan menyimpan ke Supabase."""
    
    try:
        data = request.json
        chat_history = data.get('chatHistory', [])
        session_id = data.get('sessionId')
        patient_data = data.get('patientData', {})

        if not chat_history or not session_id:
            return jsonify({"error": "Data chat atau sessionId tidak ada"}), 400

        # Simpan ke Supabase (primary storage)
        success = utils.save_chat_history_supabase(session_id, chat_history, patient_data)
        
        if success:
            return jsonify({"message": f"Chat disimpan ke Supabase dengan session ID: {session_id}"}), 200
        else:
            return jsonify({"error": "Gagal menyimpan chat ke Supabase"}), 500
            
    except Exception as e:
        print(f"Error saving chat: {e}")
        return jsonify({"error": "Gagal menyimpan chat di server"}), 500

# === Vercel Serverless Function ===
# Vercel expects the Flask app to be available as 'app'
# The if __name__ == '__main__' block is not needed for Vercel