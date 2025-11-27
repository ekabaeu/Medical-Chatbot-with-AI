# Backend Documentation

This document provides detailed information about the backend components of the Medical Chatbot application.

## Table of Contents

- [Application Architecture](#application-architecture)
- [Main Application (app.py)](#main-application-apppy)
- [Utility Functions (utils.py)](#utility-functions-utilspy)
- [PDF Processing (pdf_processor.py)](#pdf-processing-pdf_processorpy)
- [System Prompts (prompts.py)](#system-prompts-promptspy)
- [API Endpoints](#api-endpoints)
- [Data Flow](#data-flow)

## Application Architecture

The backend is built using Flask, a lightweight Python web framework. It follows a three-stage diagnostic process:

1. **Information Collection**: Gather initial patient information
2. **Symptom Analysis**: Ask targeted diagnostic questions
3. **Medical Recommendation**: Provide analysis and recommendations

The application integrates with:
- **Chutes AI API** for natural language processing
- **Supabase** for data storage
- **ICD-11 API** for medical classification
- **PDF processing libraries** for laboratory results analysis

## Main Application (app.py)

The main Flask application that handles HTTP requests and orchestrates the chatbot functionality.

### Key Components

#### Flask Setup
```python
app = Flask(__name__)
CORS(app)
```

#### Streaming Response Handler
```python
def stream_chutes_ai_response(payload)
```
- Handles streaming responses from Chutes AI API
- Processes and formats response chunks
- Implements error handling for API connectivity issues

#### Patient Data Handler
```python
def handle_patient_data_request(message)
```
- Extracts patient ID from messages
- Retrieves patient data from database
- Formats and returns patient information

#### ICD-11 Context Handler
```python
def get_icd11_context(user_message)
```
- Extracts medical terms from user messages
- Queries ICD-11 API for medical context
- Formats context for AI processing

### API Endpoints

#### POST /chat
Main endpoint for processing chat messages through the three-stage diagnostic system.

**Logic Flow:**
1. Receives chat history from frontend
2. Determines current stage based on message count
3. Selects appropriate system prompt
4. Sends request to Chutes AI API
5. Streams response back to frontend
6. Saves patient data on first message

#### POST /save-chat
Endpoint for saving chat history to Supabase database.

**Logic Flow:**
1. Receives chat history and session data
2. Saves data to Supabase `chat_logs` table
3. Updates existing records if session ID already exists

#### POST /process-pdf
Endpoint for processing laboratory result PDF files.

**Logic Flow:**
1. Receives PDF file upload
2. Validates file format and content
3. Processes PDF through multiple extraction methods
4. Cleans and analyzes extracted text
5. Extracts laboratory values
6. Retrieves ICD-11 context for medical terms
7. Generates AI-powered summary
8. Saves results to Supabase
9. Returns summary and values to frontend

## Utility Functions (utils.py)

Contains helper functions for data processing and database operations.

### Patient Data Functions

#### generate_patient_id()
Generates a random alphanumeric patient ID.

#### extract_patient_info(message)
Extracts patient information from initial message using regex patterns:
- Name (first word in message)
- Age (number followed by "tahun" or "thn")
- Gender (laki-laki, perempuan, pria, wanita)

#### save_patient_data_supabase()
Saves patient data to Supabase `patients` table.

#### get_patient_data_by_id()
Retrieves patient data from Supabase by patient ID with variant matching.

### Chat History Functions

#### save_chat_history_supabase()
Saves or updates chat history in Supabase `chat_logs` table.

### Laboratory Results Functions

#### save_lab_results_supabase()
Saves laboratory results data to Supabase `lab_results` table:
- Session ID for association with chat session
- Original PDF filename
- PDF file content as bytes
- Extracted text from PDF
- Parsed laboratory values
- AI-generated summary

### ICD-11 Integration Functions

#### search_icd11_entities()
Searches ICD-11 database for medical terms.

#### get_icd11_entity_details()
Retrieves detailed information about specific ICD-11 entities.

## PDF Processing (pdf_processor.py)

Handles the complete processing pipeline for laboratory result PDFs.

### Text Extraction Functions

#### extract_text_from_pdf()
Extracts text from PDF files using multiple fallback methods:
1. **pdfplumber**: Primary method for high-quality text extraction
2. **PyPDF2**: Fallback for compatibility with different PDF formats
3. **OCR**: Final fallback for scanned documents using pytesseract

#### extract_text_with_ocr()
Extracts text from PDF files using Optical Character Recognition:
- Converts PDF pages to images
- Applies OCR using pytesseract
- Supports Indonesian language text

### Text Processing Functions

#### clean_lab_results_text()
Cleans extracted text by removing irrelevant information:
- Headers and footers
- Contact information
- Page numbers
- Boilerplate text

#### extract_lab_values()
Extracts laboratory values from cleaned text using regex patterns:
- Matches format: "Parameter: Value Unit"
- Returns structured data with parameter names, values, and units

### Analysis Functions

#### _get_icd11_context_for_terms()
Retrieves ICD-11 context for medical terms identified in lab results:
- Searches ICD-11 database for each term
- Retrieves entity details and definitions
- Formats context for AI processing

#### summarize_lab_results()
Generates AI-powered summary of laboratory results:
- Combines extracted text with ICD-11 context
- Sends request to Chutes AI API
- Returns human-readable summary with medical insights

#### process_lab_pdf()
Orchestrates the complete PDF processing pipeline:
1. Extracts text from PDF
2. Cleans extracted text
3. Extracts laboratory values
4. Retrieves ICD-11 context
5. Generates AI summary
6. Returns structured results

## System Prompts (prompts.py)

Contains system prompts that guide the AI's behavior in different consultation stages.

### Stage 1: Information Collection
Focuses on asking exactly 3 diagnostic questions to clarify the initial complaint.

### Stage 2: Symptom Analysis
Provides comprehensive medical analysis including:
- Medical analysis based on all collected data
- Possible causes with explanations
- Clear recommendations

### Stage 3: Natural Conversation
Enables natural follow-up conversations while restricting to medical topics only.

## API Endpoints

### /chat (POST)

**Request Headers:**
- Content-Type: application/json

**Request Body:**
```json
{
  "history": [
    {
      "timestamp": "ISO timestamp",
      "sender": "User|Bot",
      "message": "Message content"
    }
  ],
  "sessionId": "unique session identifier"
}
```

**Response:**
- Streaming text response
- Custom headers with patient data and session ID

### /save-chat (POST)

**Request Headers:**
- Content-Type: application/json

**Request Body:**
```json
{
  "chatHistory": [...],
  "sessionId": "session_id",
  "patientData": {...}
}
```

**Response:**
```json
{
  "message": "Chat saved successfully"
}
```

### /process-pdf (POST)

**Request Headers:**
- Content-Type: multipart/form-data

**Request Body:**
- `pdf`: PDF file to process
- `session_id`: (optional) Session identifier

**Response:**
```json
{
  "summary": "AI-generated summary of lab results",
  "lab_values": {
    "Glukosa": {
      "value": "90",
      "unit": "mg/dL"
    }
  }
}
```

## Data Flow

### Initial Consultation Flow
1. User sends initial complaint
2. Frontend sends message to `/chat`
3. Backend extracts patient info and generates ID
4. Patient data saved to Supabase
5. Request sent to Chutes AI with Stage 1 prompt
6. Response streamed back to frontend
7. Chat history automatically saved

### Follow-up Conversation Flow
1. User sends additional messages
2. Message count determines consultation stage
3. Appropriate system prompt selected
4. Request sent to Chutes AI
5. Response streamed back to frontend
6. Chat history automatically updated

### Data Storage Flow
1. Patient data saved to `patients` table on first message
2. Chat history saved to `chat_logs` table after each interaction
3. Automatic updates for existing session IDs

### Laboratory Results Processing Flow
1. User uploads PDF laboratory results
2. Frontend sends file to `/process-pdf`
3. Backend processes PDF through multiple extraction methods
4. Text is cleaned and analyzed
5. Laboratory values are extracted
6. ICD-11 context is retrieved for medical terms
7. AI summary is generated
8. Results saved to `lab_results` table
9. Summary and values returned to frontend