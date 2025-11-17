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
        potential_name = words[0]
        # Kapitalisasi huruf pertama
        info['nama'] = potential_name.capitalize()

    return info

def escape_csv(value):
    """Meng-escape string untuk CSV agar aman jika mengandung koma atau kutip."""
    if not isinstance(value, str):
        return value
    if ',' in value or '"' in value or '\n' in value:
        return '"' + value.replace('"', '""') + '"'
    return value

def save_patient_data(patient_id: str, name: str, age: int, gender: str, initial_complaint: str):
    """
    Menyimpan data satu pasien ke dalam file database.csv.
    Jika file belum ada, fungsi ini akan membuatnya dan menulis header.
    Jika file sudah ada, fungsi ini akan menambahkan data baru di baris terakhir.

    Args:
        patient_id (str): ID unik untuk pasien.
        name (str): Nama lengkap pasien.
        age (int): Umur pasien.
        gender (str): Jenis kelamin pasien.
        initial_complaint (str): Keluhan awal yang disampaikan pasien.
    """
    file_path = 'database.csv'
    # Menentukan header untuk file CSV
    header = ['id_pasien', 'nama', 'umur', 'gender', 'keluhan_awal']
    
    # Cek apakah file sudah ada untuk menentukan perlu menulis header atau tidak
    file_exists = os.path.isfile(file_path)

    # Data pasien dalam bentuk dictionary
    patient_data = {
        'id_pasien': patient_id,
        'nama': name,
        'umur': age,
        'gender': gender,
        'keluhan_awal': initial_complaint
    }
    
    # Membuka file dalam mode 'a' (append)
    try:
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            
            # Jika file baru dibuat atau kosong, tulis header terlebih dahulu
            if not file_exists or os.path.getsize(file_path) == 0:
                writer.writeheader()
            
            # Tulis data pasien
            writer.writerow(patient_data)
            
        print(f"Data untuk pasien '{name}' ({patient_id}) telah berhasil disimpan.")
        return True
    except IOError as e:
        print(f"Terjadi error saat menulis ke file: {e}")
        return False

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
            print(f"Data untuk pasien '{name}' ({patient_id}) telah berhasil disimpan ke Supabase.")
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
        
        # Logging untuk debugging - cek apakah sudah ada data dengan session_id ini
        print(f"Menyimpan chat history untuk session_id: {session_id}")
        existing_data = supabase.table('chat_logs').select('*').eq('session_id', session_id).execute()
        print(f"Data yang sudah ada dengan session_id {session_id}: {existing_data.data}")
        
        chat_data = {
            'session_id': session_id,
            'chat_history': chat_history,
            'patient_data': patient_data
        }
        
        # Jika sudah ada data dengan session_id ini, update daripada insert
        if existing_data.data:
            print(f"Updating existing chat log for session_id: {session_id}")
            response = supabase.table('chat_logs').update(chat_data).eq('session_id', session_id).execute()
        else:
            print(f"Inserting new chat log for session_id: {session_id}")
            response = supabase.table('chat_logs').insert(chat_data).execute()
            
        if response.data:
            print(f"Riwayat chat untuk sesi '{session_id}' telah berhasil disimpan ke Supabase.")
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
            print(f"Mencoba varian ID: '{variant}'")  # Logging tambahan
            # Query data pasien berdasarkan id_pasien
            response = supabase.table('patients').select('*').eq('id_pasien', variant).execute()
            
            print(f"Respons dari Supabase untuk varian '{variant}': {response}")  # Logging tambahan
            
            # Periksa apakah ada data yang ditemukan
            if response.data and len(response.data) > 0:
                print(f"Data ditemukan: {response.data[0]}")  # Logging tambahan
                # Kembalikan data pasien pertama yang ditemukan
                return response.data[0]
        
        # Jika masih tidak ditemukan, coba tanpa filter spesifik
        print("Mencoba pencarian tanpa filter spesifik...")
        response = supabase.table('patients').select('*').execute()
        print(f"Semua data dalam tabel: {response.data}")  # Logging tambahan
        
        # Tidak ada data yang ditemukan
        print(f"Tidak ada data yang ditemukan untuk ID pasien: {patient_id}")  # Logging tambahan
        return None
    except Exception as e:
        print(f"Terjadi error saat mengambil data pasien dari Supabase: {e}")
        import traceback
        traceback.print_exc()  # Menampilkan stack trace untuk debugging
        return None
