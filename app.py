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
MODEL_NAME = "alibayram/medgemma"
SAVE_DIR = "chat_logs"

# === Fungsi Helper untuk Mengamankan CSV ===
def escape_csv(s):
    if not s:
        return '""'
    if ',' in s or '"' in s or '\n' in s:
        return '"' + s.replace('"', '""') + '"'
    return s

# === Fungsi Helper Baru untuk Ekstraksi Data ===
def extract_patient_data(chat_history):
    """Mencari blok JSON data pasien di riwayat chat."""
    for row in chat_history:
        if row.get('sender') == 'Bot':
            message = row.get('message', '')
            # Cari baris yang dimulai dengan blok JSON kita
            # Kita harus periksa baris pertama dari setiap pesan
            if message.strip().startswith('{"PATIENT_DATA":'):
                try:
                    # Ambil hanya baris JSON pertama
                    json_line = message.split('\n')[0]
                    data = json.loads(json_line)
                    return data.get('PATIENT_DATA') # Mengembalikan {'nama': 'Eka', ...}
                except json.JSONDecodeError:
                    # Gagal parse, abaikan
                    pass
    return None # Tidak ditemukan

# === SYSTEM PROMPT BARU (Logika Pengumpul Data) ===
system_prompt = {
    "role": "system",
    "content": (
        "Anda adalah Asisten Medis AI dengan dua tugas. Anda HARUS mengikuti urutan tugas ini:"
        "\n\n"
        "**TUGAS 1: PENGUMPULAN DATA**"
        "\n"
        "Misi pertama Anda adalah mengumpulkan 4 data: `Nama`, `Umur`, `Gender`, dan `Keluhan Awal`."
        "Lihat riwayat chat. Jika 4 data ini BELUM LENGKAP, Anda HARUS menanyakannya. JANGAN lakukan analisis medis."
        "\n"
        "* **Jika User baru menyapa ('Halo'):** Jawab, 'Halo. Untuk memulai sesi konsultasi, boleh saya tahu Nama, Umur, Gender, dan Keluhan Awal Anda?'"
        "\n"
        "* **Jika User memberi sebagian data ('Saya sakit perut'):** Jawab, 'Saya catat keluhannya (sakit perut). Untuk melengkapi data, boleh saya tahu Nama, Umur, dan Gender Anda?'"
        "\n"
        "* **Jika User menolak memberi data:** Ulangi dengan sopan bahwa data diperlukan untuk memulai."
        "\n\n"
        "**TUGAS 2: ANALISIS MEDIS (SETELAH DATA LENGKAP)**"
        "\n"
        "SEGERA setelah Anda mengkonfirmasi 4 data (Nama, Umur, Gender, Keluhan), Anda HARUS melakukan dua hal dalam SATU respons:"
        "\n"
        "1. **KIRIM BLOK JSON:** Di baris PERTAMA, keluarkan blok JSON terstruktur yang berisi data pasien. HARUS dalam format ini (JANGAN tambahkan teks lain di baris ini):"
        "\n"
        "   `{\"PATIENT_DATA\": {\"nama\": \"[NAMA PASIEN]\", \"umur\": \"[UMUR PASIEN]\", \"gender\": \"[GENDER PASIEN]\", \"keluhan_awal\": \"[KELUHAN AWAL PASIEN]\"}}`"
        "\n"
        "2. **LANJUTKAN ANALISIS:** Setelah blok JSON (di baris baru), lanjutkan dengan analisis medis Anda menggunakan format Markdown terstruktur di bawah ini."
        "\n\n"
        "**Contoh Respons TUGAS 2 (JSON + Analisis):**"
        "\n"
        "   `{\"PATIENT_DATA\": {\"nama\": \"Eka\", \"umur\": \"30\", \"gender\": \"Pria\", \"keluhan_awal\": \"Sakit perut parah\"}}`"
        "\n"
        "**Analisis Awal:**\nBaik Eka, 'Sakit perut parah' adalah keluhan yang... [Analisis Anda...]\n\n"
        "--- (FORMAT ANALISIS MEDIS) ---"
        "\n"
        "**Analisis Awal:**\n[Analisis Anda...]\n\n"
        "**Kemungkinan Penyebab:**\n* **[Penyebab 1]:** [Penjelasan...]\n* **[Penyebab 2]:** [Penjelasan...]\n\n"
        "**Pertanyaan Diagnostik Lanjutan:**\n* [Pertanyaan 1?]\n* [Pertanyaan 2?]\n\n"
        "**Rekomendasi Awal:**\n* [Rekomendasi...]"
        "\n\n"
        "**ATURAN TAMBAHAN:**"
        "\n"
        "Jika kapan saja pengguna bertanya pertanyaan non-medis (cuaca, film, sejarah), JAWAB HANYA DENGAN: 'Maaf, saya adalah asisten medis AI dan hanya dapat memproses pertanyaan terkait kesehatan.'"
    )
}

# === Endpoint 1: Untuk Streaming Chat (Tidak Berubah) ===
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
        messages_for_llm.append({
            "role": role,
            "content": chat.get('message')
        })

    final_payload_messages = [system_prompt] + messages_for_llm

    payload = {
        "model": MODEL_NAME,
        "messages": final_payload_messages,
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

# === Endpoint 2: Untuk Menyimpan Chat (MODIFIKASI BESAR) ===
@app.route('/save-chat', methods=['POST'])
def save_chat():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    try:
        data = request.json
        chat_history = data.get('chatHistory', [])

        if not chat_history:
            return jsonify({"error": "Tidak ada data chat"}), 400

        # --- PERUBAHAN UTAMA: Ekstraksi data dari riwayat ---
        patient_data = extract_patient_data(chat_history)
        
        csv_content = []
        
        # Tentukan nama file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_log_{timestamp}.csv" # Default
        
        if patient_data:
            # Jika data terstruktur ditemukan, gunakan untuk header CSV
            csv_content.append(f"Nama Pasien,{escape_csv(patient_data.get('nama'))}\n")
            csv_content.append(f"Umur,{escape_csv(patient_data.get('umur'))}\n")
            csv_content.append(f"Gender,{escape_csv(patient_data.get('gender'))}\n")
            csv_content.append(f"Keluhan Awal,{escape_csv(patient_data.get('keluhan_awal'))}\n\n")
            
            # Gunakan nama pasien untuk nama file
            patient_name = patient_data.get('nama', 'pasien').replace(' ', '_')
            filename = f"chat_{patient_name}_{timestamp}.csv"
        else:
            # Jika tidak ada data terstruktur, simpan sebagai log mentah
            csv_content.append("Log Mentah (Data Pasien Tidak Terdeteksi/Belum Lengkap)\n\n")

        # Tambahkan header riwayat chat
        csv_content.append("Timestamp,Sender,Message\n")
        
        for row in chat_history:
            # Kita bersihkan JSON dari log agar CSV lebih rapi
            message_to_save = row.get('message', '')
            if message_to_save.strip().startswith('{"PATIENT_DATA":'):
                # Pisahkan JSON dari sisa pesan
                parts = message_to_save.split('\n', 1)
                if len(parts) > 1:
                    message_to_save = parts[1] # Simpan sisa pesannya
                else:
                    message_to_save = "[Blok Data Pasien]" # Jika hanya JSON
            
            line = f"{row.get('timestamp')},{row.get('sender')},{escape_csv(message_to_save)}\n"
            csv_content.append(line)
        
        csv_string = "".join(csv_content)
        
        filepath = os.path.join(SAVE_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(csv_string)
        
        return jsonify({"message": f"Chat disimpan sebagai {filename}"}), 200

    except Exception as e:
        print(f"Error saving chat: {e}")
        return jsonify({"error": "Gagal menyimpan chat di server"}), 500

# === Jalankan Server ===
if __name__ == '__main__':
    app.run(debug=True, port=5000)