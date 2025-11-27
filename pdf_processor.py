import PyPDF2
import pdfplumber
import io
import re
from typing import Optional, Dict, Any
import config
import traceback
import json
import requests
import pytesseract
from PIL import Image
import tempfile
import os
from utils import search_icd11_entities, get_icd11_entity_details


def extract_text_from_pdf(file_stream) -> str:
    """
    Mengekstrak teks dari file PDF menggunakan pdfplumber untuk akurasi yang lebih baik.
    Jika ekstraksi teks gagal, gunakan OCR sebagai fallback.
    
    Args:
        file_stream: Stream file PDF
        
    Returns:
        str: Teks yang diekstrak dari PDF
    """
    # Reset stream position to beginning
    file_stream.seek(0)
    
    # Coba ekstrak teks dengan pdfplumber terlebih dahulu
    try:
        with pdfplumber.open(file_stream) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            if text.strip():
                return text.strip()
    except Exception as e:
        print(f"Error extracting text with pdfplumber: {e}")
    
    # Fallback ke PyPDF2 jika pdfplumber gagal
    try:
        file_stream.seek(0)
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Error extracting text with PyPDF2: {e}")
    
    # Fallback ke OCR jika ekstraksi teks biasa gagal
    try:
        return extract_text_with_ocr(file_stream).strip()
    except Exception as e:
        print(f"Error extracting text with OCR: {e}")
        raise Exception(f"Gagal mengekstrak teks dari PDF: {e}")


def extract_text_with_ocr(file_stream) -> str:
    """
    Mengekstrak teks dari file PDF menggunakan OCR (Optical Character Recognition).
    
    Args:
        file_stream: Stream file PDF
        
    Returns:
        str: Teks yang diekstrak dari PDF menggunakan OCR
    """
    import pdf2image
    
    # Reset stream position to beginning
    file_stream.seek(0)
    
    # Simpan file sementara
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(file_stream.read())
        tmp_file_path = tmp_file.name
    
    try:
        # Konversi PDF ke gambar
        images = pdf2image.convert_from_path(tmp_file_path)
        
        # Ekstrak teks dari setiap halaman menggunakan OCR
        text = ""
        for image in images:
            # Gunakan pytesseract untuk OCR
            page_text = pytesseract.image_to_string(image, lang='ind')
            text += page_text + "\n"
        
        return text
    finally:
        # Hapus file sementara
        os.unlink(tmp_file_path)


def clean_lab_results_text(text: str) -> str:
    """
    Membersihkan teks hasil laboratorium untuk menghilangkan informasi yang tidak relevan.
    
    Args:
        text (str): Teks mentah dari PDF hasil laboratorium
        
    Returns:
        str: Teks yang telah dibersihkan
    """
    # Hapus header dan footer umum
    skip_keywords = ['laboratorium', 'hasil pemeriksaan', 'tanggal cetak',
                     'no. registrasi', 'alamat', 'telepon', 'page']
    
    cleaned_lines = [
        line for line in text.split('\n')
        if line.strip() and not any(keyword in line.lower() for keyword in skip_keywords)
    ]
    
    return '\n'.join(cleaned_lines)


def extract_lab_values(text: str) -> Dict[str, Any]:
    """
    Mengekstrak nilai-nilai penting dari teks hasil laboratorium.
    
    Args:
        text (str): Teks hasil laboratorium yang telah dibersihkan
        
    Returns:
        dict: Dictionary berisi nilai-nilai hasil laboratorium
    """
    # Pola untuk mencocokkan nilai laboratorium (contoh: Glukosa: 90 mg/dL)
    pattern = r'([A-Za-z\s]+):\s*([0-9.,]+)\s*([A-Za-z/\s]+)'
    matches = re.findall(pattern, text)
    
    return {
        match[0].strip(): {
            'value': match[1].strip(),
            'unit': match[2].strip()
        }
        for match in matches
    }


def summarize_lab_results(lab_text: str, lab_values: dict) -> str:
    """
    Menggunakan AI untuk merangkum hasil laboratorium dengan integrasi informasi ICD-11.
    
    Args:
        lab_text (str): Teks hasil laboratorium yang telah dibersihkan
        lab_values (dict): Dictionary berisi nilai-nilai hasil laboratorium
        
    Returns:
        str: Rangkuman hasil laboratorium dengan konteks ICD-11
    """
    # Ekstrak istilah medis dari lab_values
    medical_terms = list(lab_values.keys())[:3]  # Batasi 3 istilah pertama
    
    # Cari konteks ICD-11
    icd11_context = ""
    for term in medical_terms:
        try:
            search_results = search_icd11_entities(term)
            if search_results and 'destinationEntities' in search_results:
                entities = search_results['destinationEntities'][:1]
                for entity in entities:
                    title = entity.get('title', 'Unknown')
                    if 'id' in entity:
                        entity_id = entity['id'].split('/')[-1]
                        if entity_id:
                            try:
                                entity_details = get_icd11_entity_details(entity_id)
                                definition = entity_details.get('definition', {}).get('@value', '')
                                if definition:
                                    icd11_context += f"- {title}: {definition}\n"
                                else:
                                    icd11_context += f"- {title}\n"
                            except Exception:
                                # Jika tidak bisa mendapatkan detail, gunakan hanya judul
                                icd11_context += f"- {title}\n"
        except Exception as e:
            print(f"Error fetching ICD-11 context for term '{term}': {e}")
            continue
    
    # Buat prompt untuk AI dengan konteks ICD-11
    prompt = f"""
    Anda adalah seorang asisten medis AI yang membantu dalam menganalisis hasil laboratorium pasien.
    Berikut adalah hasil pemeriksaan laboratorium pasien:
    
    {lab_text}
    
    Informasi ICD-11 terkait parameter laboratorium:
    {icd11_context}
    
    Tugas Anda:
    1. Rangkum hasil laboratorium tersebut dalam bentuk yang mudah dipahami
    2. Jelaskan apakah nilai-nilai tersebut normal atau tidak berdasarkan standar medis umum
    3. Jika ada nilai yang abnormal, berikan penjelasan singkat tentang kemungkinan implikasinya
    4. Hubungkan hasil dengan informasi ICD-11 yang tersedia
    5. Berikan rekomendasi umum untuk tindak lanjut (jika diperlukan)
    
    Berikan respons dalam bahasa Indonesia yang jelas dan informatif.
    """
    
    # Buat payload untuk API Chutes AI
    payload = {
        "model": config.MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Anda adalah asisten medis AI yang ahli dalam menganalisis hasil laboratorium dengan konteks ICD-11."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "max_tokens": 1024,
        "temperature": 0.5
    }
    
    # Kirim permintaan ke API Chutes AI
    headers = {
        "Authorization": f"Bearer {config.CHUTES_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(config.CHUTES_API_URL, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        result = response.json()
        
        return result.get("choices", [{}])[0].get("message", {}).get("content", "Gagal membuat rangkuman.")
    except Exception as e:
        print(f"Error summarizing lab results: {e}")
        return f"Terjadi kesalahan saat merangkum hasil laboratorium: {str(e)}"


def process_lab_pdf(file_stream) -> Dict[str, Any]:
    """
    Memproses file PDF hasil laboratorium secara lengkap.
    
    Args:
        file_stream: Stream file PDF
        
    Returns:
        dict: Dictionary berisi teks mentah, teks yang dibersihkan, nilai laboratorium, dan rangkuman
    """
    # Reset stream position to beginning
    file_stream.seek(0)
    
    # Ekstrak teks dari PDF
    raw_text = extract_text_from_pdf(file_stream)
    
    # Bersihkan teks
    cleaned_text = clean_lab_results_text(raw_text)
    
    # Ekstrak nilai laboratorium
    lab_values = extract_lab_values(cleaned_text)
    
    # Rangkum hasil dengan AI
    summary = summarize_lab_results(cleaned_text, lab_values)
    
    return {
        'raw_text': raw_text,
        'cleaned_text': cleaned_text,
        'lab_values': lab_values,
        'summary': summary
    }