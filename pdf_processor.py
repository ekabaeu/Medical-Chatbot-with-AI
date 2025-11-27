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


def extract_text_from_pdf(file_stream) -> str:
    """
    Mengekstrak teks dari file PDF menggunakan pdfplumber untuk akurasi yang lebih baik.
    Jika ekstraksi teks gagal, gunakan OCR sebagai fallback.
    
    Args:
        file_stream: Stream file PDF
        
    Returns:
        str: Teks yang diekstrak dari PDF
    """
    text = ""
    try:
        # Reset stream position to beginning
        file_stream.seek(0)
        # Gunakan pdfplumber untuk ekstraksi teks yang lebih akurat
        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text with pdfplumber: {e}")
        traceback.print_exc()
        # Fallback ke PyPDF2 jika pdfplumber gagal
        try:
            file_stream.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_stream)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e2:
            print(f"Error extracting text with PyPDF2: {e2}")
            traceback.print_exc()
            # Fallback ke OCR jika ekstraksi teks biasa gagal
            try:
                text = extract_text_with_ocr(file_stream)
            except Exception as e3:
                print(f"Error extracting text with OCR: {e3}")
                traceback.print_exc()
                raise Exception(f"Gagal mengekstrak teks dari PDF: {e3}")
    
    return text.strip()


def extract_text_with_ocr(file_stream) -> str:
    """
    Mengekstrak teks dari file PDF menggunakan OCR (Optical Character Recognition).
    
    Args:
        file_stream: Stream file PDF
        
    Returns:
        str: Teks yang diekstrak dari PDF menggunakan OCR
    """
    try:
        import pdf2image
        # Reset stream position to beginning
        file_stream.seek(0)
        
        # Simpan file sementara
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(file_stream.read())
            tmp_file_path = tmp_file.name
        
        # Konversi PDF ke gambar
        images = pdf2image.convert_from_path(tmp_file_path)
        
        # Ekstrak teks dari setiap halaman menggunakan OCR
        text = ""
        for image in images:
            # Gunakan pytesseract untuk OCR
            page_text = pytesseract.image_to_string(image, lang='ind')
            text += page_text + "\n"
        
        # Hapus file sementara
        os.unlink(tmp_file_path)
        
        return text.strip()
    except Exception as e:
        print(f"Error extracting text with OCR: {e}")
        traceback.print_exc()
        raise Exception(f"Gagal mengekstrak teks dari PDF menggunakan OCR: {e}")


def clean_lab_results_text(text: str) -> str:
    """
    Membersihkan teks hasil laboratorium untuk menghilangkan informasi yang tidak relevan.
    
    Args:
        text (str): Teks mentah dari PDF hasil laboratorium
        
    Returns:
        str: Teks yang telah dibersihkan
    """
    # Hapus header dan footer umum
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Lewati baris yang mengandung informasi header/footer umum
        if any(keyword in line.lower() for keyword in [
            'laboratorium', 'hasil pemeriksaan', 'tanggal cetak', 
            'no. registrasi', 'alamat', 'telepon', 'page'
        ]):
            continue
        # Lewati baris kosong
        if line.strip() == '':
            continue
        cleaned_lines.append(line)
    
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
    
    lab_values = {}
    for match in matches:
        test_name = match[0].strip()
        value = match[1].strip()
        unit = match[2].strip()
        lab_values[test_name] = {
            'value': value,
            'unit': unit
        }
    
    return lab_values


def summarize_lab_results(lab_text: str) -> str:
    """
    Menggunakan AI untuk merangkum hasil laboratorium.
    
    Args:
        lab_text (str): Teks hasil laboratorium yang telah dibersihkan
        
    Returns:
        str: Rangkuman hasil laboratorium
    """
    # Buat prompt untuk AI
    prompt = f"""
    Anda adalah seorang asisten medis AI yang membantu dalam menganalisis hasil laboratorium pasien.
    Berikut adalah hasil pemeriksaan laboratorium pasien:
    
    {lab_text}
    
    Tugas Anda:
    1. Rangkum hasil laboratorium tersebut dalam bentuk yang mudah dipahami
    2. Jelaskan apakah nilai-nilai tersebut normal atau tidak berdasarkan standar medis umum
    3. Jika ada nilai yang abnormal, berikan penjelasan singkat tentang kemungkinan implikasinya
    4. Berikan rekomendasi umum untuk tindak lanjut (jika diperlukan)
    
    Berikan respons dalam bahasa Indonesia yang jelas dan informatif.
    """
    
    # Buat payload untuk API Chutes AI
    payload = {
        "model": config.MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Anda adalah asisten medis AI yang ahli dalam menganalisis hasil laboratorium."},
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
        
        if result.get("choices") and len(result["choices"]) > 0:
            return result["choices"][0].get("message", {}).get("content", "Gagal membuat rangkuman.")
        else:
            return "Gagal membuat rangkuman."
    except Exception as e:
        print(f"Error summarizing lab results: {e}")
        traceback.print_exc()
        return f"Terjadi kesalahan saat merangkum hasil laboratorium: {str(e)}"


def process_lab_pdf(file_stream) -> Dict[str, Any]:
    """
    Memproses file PDF hasil laboratorium secara lengkap.
    
    Args:
        file_stream: Stream file PDF
        
    Returns:
        dict: Dictionary berisi teks mentah, teks yang dibersihkan, nilai laboratorium, dan rangkuman
    """
def process_lab_pdf(file_stream) -> Dict[str, Any]:
    """
    Memproses file PDF hasil laboratorium secara lengkap.
    
    Args:
        file_stream: Stream file PDF
        
    Returns:
        dict: Dictionary berisi teks mentah, teks yang dibersihkan, nilai laboratorium, dan rangkuman
    """
    # Debug: Cek tipe file stream
    print(f"File stream type: {type(file_stream)}")
    print(f"File stream: {file_stream}")
    
    # Reset stream position to beginning
    file_stream.seek(0)
    
    # Ekstrak teks dari PDF
    raw_text = extract_text_from_pdf(file_stream)
    
    # Bersihkan teks
    cleaned_text = clean_lab_results_text(raw_text)
    
    # Ekstrak nilai laboratorium
    lab_values = extract_lab_values(cleaned_text)
    
    # Rangkum hasil dengan AI
    summary = summarize_lab_results(cleaned_text)
    
    return {
        'raw_text': raw_text,
        'cleaned_text': cleaned_text,
        'lab_values': lab_values,
        'summary': summary
    }