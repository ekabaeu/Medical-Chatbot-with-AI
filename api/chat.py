import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import json
import requests
import os
from prompts import system_prompt_task_1, system_prompt_task_2, system_prompt_task_3
import utils
import config

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
                            pass
    except requests.exceptions.RequestException as e:
        yield f"Error: Gagal terhubung ke layanan AI. {e}"

def handler(request):
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }
    
    data = json.loads(request.body)
    history_from_frontend = data.get('history', [])
    if not history_from_frontend:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Riwayat chat kosong"})
        }

    messages_for_llm = []
    for chat_item in history_from_frontend:
        role = "user" if chat_item.get('sender') == 'User' else 'assistant'
        content = chat_item.get('message')
        if content:
            messages_for_llm.append({"role": role, "content": content})

    if messages_for_llm and messages_for_llm[-1]['role'] == 'user':
        last_user_message = messages_for_llm[-1]['content'].lower()
        non_medical_keywords = [
            '1+1', 'cuaca', 'sejarah', 'presiden', 'politik', 
            'siapa kamu', 'matematika', 'fisika', 'berapa'
        ]
        if any(keyword in last_user_message for keyword in non_medical_keywords):
            def generate_refusal():
                yield "Maaf, saya hanya dapat memproses pertanyaan terkait kesehatan."
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "text/plain",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": generate_refusal()
            }

    user_message_count = sum(1 for msg in messages_for_llm if msg['role'] == 'user')
    
    patient_info = {}
    if user_message_count == 1:
        message_content = messages_for_llm[-1]['content'].strip()
        if message_content.lower().startswith('cek '):
            patient_id = message_content[4:].strip()
            patient_data = utils.get_patient_data(patient_id)
            if patient_data:
                response_text = (
                    f"Data Pasien:\n"
                    f"ID: {patient_data['id_pasien']}\n"
                    f"Nama: {patient_data['nama']}\n"
                    f"Umur: {patient_data['umur']}\n"
                    f"Gender: {patient_data['gender']}\n"
                    f"Keluhan Awal: {patient_data['keluhan_awal']}"
                )
            else:
                response_text = "Pasien tidak ditemukan."
            
            def generate_response():
                yield response_text
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "text/plain",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": generate_response()
            }
        else:
            initial_complaint = messages_for_llm[-1]['content']
            patient_info = utils.extract_patient_info(initial_complaint)
            patient_id = utils.generate_patient_id()
            utils.save_patient_data(
                patient_id=patient_id,
                name=patient_info['nama'],
                age=patient_info['umur'],
                gender=patient_info['gender'],
                initial_complaint=initial_complaint
            )
            final_system_prompt = system_prompt_task_1
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
    
    response_headers = {
        "Content-Type": "text/plain",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if patient_info:
        response_headers["X-Patient-Data"] = json.dumps(patient_info)
        response_headers["Access-Control-Expose-Headers"] = "X-Patient-Data"

    return {
        "statusCode": 200,
        "headers": response_headers,
        "body": stream_chutes_ai_response(payload)
    }