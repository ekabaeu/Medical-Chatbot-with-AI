# File ini digunakan untuk menguji fungsi penyimpanan data pasien
# dengan menambahkan data baru setiap kali dijalankan, tanpa menghapus data lama.

from utils import save_patient_data
import time

def run_test():
    """
    Menjalankan tes untuk menambahkan data pasien baru ke database.csv.
    ID Pasien dibuat unik menggunakan timestamp agar tidak duplikat.
    """
    print("--- Menjalankan Proses Penambahan Data Pasien Baru ---")

    # Membuat ID Pasien unik berdasarkan waktu saat ini
    # Ini untuk memastikan setiap kali tes dijalankan, ID-nya berbeda.
    patient_id_1 = f"P{int(time.time())}"
    patient_id_2 = f"P{int(time.time()) + 1}"

    # Tes Pasien 1
    print(f"\nMenyimpan data Pasien 1 (ID: {patient_id_1})...")
    save_patient_data(
        patient_id=patient_id_1,
        name='Pasien Baru Satu',
        age=42,
        gender='Laki-laki',
        initial_complaint='Batuk kering.'
    )

    # Tes Pasien 2
    print(f"\nMenyimpan data Pasien 2 (ID: {patient_id_2})...")
    save_patient_data(
        patient_id=patient_id_2,
        name='Pasien Baru Dua',
        age=31,
        gender='Perempuan',
        initial_complaint='Sakit punggung bawah.'
    )
    
    print("\n--- Proses Selesai ---")
    print("Data baru seharusnya sudah ditambahkan ke 'database.csv'.")

if __name__ == '__main__':
    run_test()
