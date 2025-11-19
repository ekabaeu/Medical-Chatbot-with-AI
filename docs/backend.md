# Backend Documentation

This document provides detailed information about the backend components of the Medical Chatbot application.

## Table of Contents

- [Application Architecture](#application-architecture)
- [Main Application (app.py)](#main-application-apppy)
- [Utility Functions (utils.py)](#utility-functions-utilspy)
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