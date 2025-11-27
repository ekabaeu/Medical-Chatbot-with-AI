import PyPDF2
import pdfplumber
import re
from typing import Dict, Any
import config
import requests
import pytesseract
import tempfile
import os
from utils import search_icd11_entities, get_icd11_entity_details


def extract_text_from_pdf(file_stream) -> str:
    """Extract text from PDF using multiple methods as fallbacks."""
    file_stream.seek(0)
    
    # Try pdfplumber first
    try:
        with pdfplumber.open(file_stream) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            if text.strip():
                return text.strip()
    except Exception:
        pass
    
    # Fallback to PyPDF2
    try:
        file_stream.seek(0)
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
        if text.strip():
            return text.strip()
    except Exception:
        pass
    
    # Final fallback to OCR
    try:
        return extract_text_with_ocr(file_stream).strip()
    except Exception as e:
        raise Exception(f"Gagal mengekstrak teks dari PDF: {e}")


def extract_text_with_ocr(file_stream) -> str:
    """Extract text from PDF using OCR."""
    import pdf2image
    
    file_stream.seek(0)
    
    # Save temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(file_stream.read())
        tmp_file_path = tmp_file.name
    
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_path(tmp_file_path)
        
        # Extract text from each page using OCR
        text = ""
        for image in images:
            page_text = pytesseract.image_to_string(image, lang='ind')
            text += page_text + "\n"
        
        return text
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)


def clean_lab_results_text(text: str) -> str:
    """Clean lab results text by removing irrelevant information."""
    skip_keywords = ['laboratorium', 'hasil pemeriksaan', 'tanggal cetak',
                     'no. registrasi', 'alamat', 'telepon', 'page']
    
    cleaned_lines = [
        line for line in text.split('\n')
        if line.strip() and not any(keyword in line.lower() for keyword in skip_keywords)
    ]
    
    return '\n'.join(cleaned_lines)


def extract_lab_values(text: str) -> Dict[str, Any]:
    """Extract important values from lab results text."""
    pattern = r'([A-Za-z\s]+):\s*([0-9.,]+)\s*([A-Za-z/\s]+)'
    matches = re.findall(pattern, text)
    
    return {
        match[0].strip(): {
            'value': match[1].strip(),
            'unit': match[2].strip()
        }
        for match in matches
    }


def _get_icd11_context_for_terms(terms: list) -> str:
    """Get ICD-11 context for medical terms."""
    context = ""
    for term in terms:
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
                                context += f"- {title}: {definition}\n" if definition else f"- {title}\n"
                            except Exception:
                                context += f"- {title}\n"
        except Exception:
            continue
    
    return context.strip()


def summarize_lab_results(lab_text: str, lab_values: dict) -> str:
    """Summarize lab results with ICD-11 context using AI."""
    # Get ICD-11 context for medical terms
    medical_terms = list(lab_values.keys())[:3]
    icd11_context = _get_icd11_context_for_terms(medical_terms)
    
    # Create AI prompt with ICD-11 context
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
    
    # Prepare API payload
    payload = {
        "model": config.MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Anda adalah asisten medis AI yang ahli dalam menganalisis hasil laboratorium dengan konteks ICD-11."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "max_tokens": 2048,
        "temperature": 0.5
    }
    
    # Send request to Chutes AI API
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
        return f"Terjadi kesalahan saat merangkum hasil laboratorium: {str(e)}"


def process_lab_pdf(file_stream) -> Dict[str, Any]:
    """Process lab PDF file completely."""
    file_stream.seek(0)
    
    # Extract text from PDF
    raw_text = extract_text_from_pdf(file_stream)
    
    # Clean text
    cleaned_text = clean_lab_results_text(raw_text)
    
    # Extract lab values
    lab_values = extract_lab_values(cleaned_text)
    
    # Summarize with AI
    summary = summarize_lab_results(cleaned_text, lab_values)
    
    return {
        'raw_text': raw_text,
        'cleaned_text': cleaned_text,
        'lab_values': lab_values,
        'summary': summary
    }