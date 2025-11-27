import csv
import os
import re
import random
import string
from config import get_supabase_client, ICD11_CLIENT_ID, ICD11_CLIENT_SECRET
from icd11_client import ICD11Client

def generate_patient_id(length=5):
    """Generate random alphanumeric patient ID with specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def extract_patient_info(message: str):
    """Extract name, age, and gender from initial message using regex."""
    info = {
        'nama': 'unknown',
        'umur': 0,
        'gender': 'unknown',
        'keluhan_awal': message.strip()
    }

    # Extract age
    age_match = re.search(r'(\d+)\s*(?:tahun|thn)', message, re.IGNORECASE)
    if age_match:
        info['umur'] = int(age_match.group(1))

    # Extract gender
    gender_match = re.search(r'\b(laki-laki|perempuan|pria|wanita)\b', message, re.IGNORECASE)
    if gender_match:
        gender = gender_match.group(1).lower()
        if gender in ['laki-laki', 'pria']:
            info['gender'] = 'Laki-laki'
        elif gender in ['perempuan', 'wanita']:
            info['gender'] = 'Perempuan'

    # Extract name
    cleaned_message = re.sub(r'(\d+)\s*(?:tahun|thn)', '', message, flags=re.IGNORECASE)
    cleaned_message = re.sub(r'\b(laki-laki|perempuan|pria|wanita)\b', '', cleaned_message, flags=re.IGNORECASE)
    cleaned_message = re.sub(r'[,.]', '', cleaned_message).strip()
    
    words = cleaned_message.split()
    if words:
        info['nama'] = words[0].capitalize()

    return info


def save_patient_data_supabase(patient_id: str, name: str, age: int, gender: str, initial_complaint: str, session_id: str = None):
    """Save patient data to Supabase Database."""
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
        return bool(response.data)
    except Exception as e:
        print(f"Error saving patient data to Supabase: {e}")
        return False

def save_lab_results_supabase(session_id: str, pdf_filename: str, original_pdf: bytes, extracted_text: str, lab_values: dict, summary: str):
    """Save lab results to Supabase Database."""
    try:
        supabase = get_supabase_client()
        
        lab_data = {
            'session_id': session_id,
            'pdf_filename': pdf_filename,
            'original_pdf': original_pdf,
            'extracted_text': extracted_text,
            'lab_values': lab_values,
            'summary': summary
        }
        
        response = supabase.table('lab_results').insert(lab_data).execute()
        return bool(response.data)
    except Exception as e:
        print(f"Error saving lab results to Supabase: {e}")
        return False

def save_chat_history_supabase(session_id: str, chat_history: list, patient_data: dict = None):
    """Save chat history to Supabase Database."""
    try:
        supabase = get_supabase_client()
        
        chat_data = {
            'session_id': session_id,
            'chat_history': chat_history,
            'patient_data': patient_data
        }
        
        # Update if session exists, otherwise insert
        existing_data = supabase.table('chat_logs').select('*').eq('session_id', session_id).execute()
        if existing_data.data:
            response = supabase.table('chat_logs').update(chat_data).eq('session_id', session_id).execute()
        else:
            response = supabase.table('chat_logs').insert(chat_data).execute()
            
        return bool(response.data)
    except Exception as e:
        print(f"Error saving chat history to Supabase: {e}")
        return False

def get_patient_data_by_id(patient_id: str):
    """Get patient data from Supabase by patient ID."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table('patients').select('*').eq('id_pasien', patient_id.strip()).execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error retrieving patient data from Supabase: {e}")
        return None

def search_icd11_entities(query: str, language: str = 'en') -> dict:
    """Search for ICD-11 entities using the provided query."""
    try:
        client = ICD11Client(
            client_id=ICD11_CLIENT_ID,
            client_secret=ICD11_CLIENT_SECRET
        )
        
        return client.search_entities(query, language)
    except Exception as e:
        print(f"Error searching ICD-11 entities: {e}")
        return {"error": str(e)}

def get_icd11_entity_details(entity_id: str, language: str = 'en') -> dict:
    """Get detailed information about a specific ICD-11 entity by ID."""
    try:
        client = ICD11Client(
            client_id=ICD11_CLIENT_ID,
            client_secret=ICD11_CLIENT_SECRET
        )
        
        return client.get_entity_by_id(entity_id, language)
    except Exception as e:
        print(f"Error getting ICD-11 entity details: {e}")
        return {"error": str(e)}
