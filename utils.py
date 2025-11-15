import csv
import os
import re
import random
import string

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