import csv
import os
import re
import random
import string
from config import get_supabase_client

def generate_patient_id(length=5):
    """Menghasilkan ID pasien acak alfanumerik dengan panjang tertentu."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def extract_patient_info(message: str):
    """
    Mengekstrak nama, umur, dan gender dari pesan awal menggunakan regex.
    Mengembalikan dictionary berisi 'nama', 'umur', dan 'gender'.
    """
    info = {
        'nama': 'unknown',
        'umur': 0,
        'gender': 'unknown'
    }

    # 1. Ekstrak Umur (lebih spesifik)
    age_match = re.search(r'(\d+)\s*(?:tahun|thn)', message, re.IGNORECASE)
    if age_match:
        info['umur'] = int(age_match.group(1))

    # 2. Ekstrak Gender
    gender_match = re.search(r'\b(laki-laki|perempuan|pria|wanita)\b', message, re.IGNORECASE)
    if gender_match:
        gender = gender_match.group(1).lower()
        if gender in ['laki-laki', 'pria']:
            info['gender'] = 'Laki-laki'
        elif gender in ['perempuan', 'wanita']:
            info['gender'] = 'Perempuan'

    # 3. Ekstrak Nama (asumsikan kata pertama adalah nama jika bukan sapaan)
    # Hapus bagian yang sudah teridentifikasi (umur, gender) untuk menyederhanakan pencarian nama
    cleaned_message = re.sub(r'(\d+)\s*(?:tahun|thn)', '', message, flags=re.IGNORECASE)
    cleaned_message = re.sub(r'\b(laki-laki|perempuan|pria|wanita)\b', '', cleaned_message, flags=re.IGNORECASE)
    
    # Hapus tanda baca umum dan spasi berlebih
    cleaned_message = re.sub(r'[,.]', '', cleaned_message).strip()
    
    # Ambil kata pertama dari pesan yang sudah dibersihkan
    words = cleaned_message.split()
    if words:
        # Asumsikan kata pertama adalah nama
        info['nama'] = words[0].capitalize()

    # Extract the actual complaint by removing patient info from the message
    complaint = message
    # Remove age pattern
    complaint = re.sub(r'(\d+)\s*(?:tahun|thn)', '', complaint, flags=re.IGNORECASE)
    # Remove gender pattern
    complaint = re.sub(r'\b(laki-laki|perempuan|pria|wanita)\b', '', complaint, flags=re.IGNORECASE)
    # Remove name (first word after cleaning)
    complaint = re.sub(r'^\s*\w+', '', complaint, 1)
    # Clean up extra spaces and punctuation
    complaint = re.sub(r'[,.\s]+', ' ', complaint).strip()
    
    # Add the extracted complaint to the info dictionary
    info['keluhan_awal'] = complaint
    return info


def save_patient_data_supabase(patient_id: str, name: str, age: int, gender: str, initial_complaint: str, session_id: str = None):
    """
    Menyimpan data pasien ke Supabase Database.
    
    Args:
        patient_id (str): ID unik untuk pasien.
        name (str): Nama lengkap pasien.
        age (int): Umur pasien.
        gender (str): Jenis kelamin pasien.
        initial_complaint (str): Keluhan awal yang disampaikan pasien.
        session_id (str): ID sesi chat (opsional).
        
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    try:
        supabase = get_supabase_client()
        patient_data = {
            'id_pasien': patient_id,
            'nama': name,
            'umur': age,
            'gender': gender,
            'keluhan_awal': initial_complaint,
            'session_id': session_id
        }
        response = supabase.table('patients').insert(patient_data).execute()
        if response.data:
            return True
        else:
            print(f"Gagal menyimpan data pasien ke Supabase: {response}")
            return False
    except Exception as e:
        print(f"Terjadi error saat menyimpan data ke Supabase: {e}")
        return False

def save_chat_history_supabase(session_id: str, chat_history: list, patient_data: dict = None):
    """
    Menyimpan riwayat chat ke Supabase Database.
    
    Args:
        session_id (str): ID sesi chat.
        chat_history (list): Daftar pesan chat.
        patient_data (dict): Data pasien (opsional).
        
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    try:
        supabase = get_supabase_client()
        
        chat_data = {
            'session_id': session_id,
            'chat_history': chat_history,
            'patient_data': patient_data
        }
        
        # Jika sudah ada data dengan session_id ini, update daripada insert
        existing_data = supabase.table('chat_logs').select('*').eq('session_id', session_id).execute()
        if existing_data.data:
            response = supabase.table('chat_logs').update(chat_data).eq('session_id', session_id).execute()
        else:
            response = supabase.table('chat_logs').insert(chat_data).execute()
            
        if response.data:
            return True
        else:
            print(f"Gagal menyimpan riwayat chat ke Supabase: {response}")
            return False
    except Exception as e:
        print(f"Terjadi error saat menyimpan riwayat chat ke Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_patient_data_by_id(patient_id: str):
    """
    Mengambil data pasien dari database Supabase berdasarkan ID pasien.
    
    Args:
        patient_id (str): ID pasien yang akan dicari.
        
    Returns:
        dict: Data pasien jika ditemukan, None jika tidak ditemukan.
    """
    try:
        supabase = get_supabase_client()
        print(f"Mencari data pasien dengan ID: {patient_id}")  # Logging tambahan
        
        # Coba beberapa varian pencarian
        variants = [
            patient_id,  # ID asli
            patient_id.strip(),  # Tanpa spasi
            patient_id.lower(),  # Huruf kecil
            patient_id.upper()   # Huruf besar
        ]
        
        for variant in variants:
            # Query data pasien berdasarkan id_pasien
            response = supabase.table('patients').select('*').eq('id_pasien', variant).execute()
            
            # Periksa apakah ada data yang ditemukan
            if response.data and len(response.data) > 0:
                # Kembalikan data pasien pertama yang ditemukan
                return response.data[0]
        
        # Tidak ada data yang ditemukan
        return None
    except Exception as e:
        print(f"Terjadi error saat mengambil data pasien dari Supabase: {e}")
        import traceback
        traceback.print_exc()  # Menampilkan stack trace untuk debugging
        return None
