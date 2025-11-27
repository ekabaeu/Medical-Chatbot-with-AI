# Medical Chatbot with AI

A Flask-based medical chatbot application that uses AI to assist patients with initial medical consultations. The application features a three-stage diagnostic process that collects patient information, analyzes symptoms, and provides medical recommendations. It also includes PDF processing capabilities for laboratory results analysis.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The Medical Chatbot with AI is designed to provide preliminary medical assistance by engaging patients in a structured conversation. The application follows a three-stage approach:

1. **Information Collection**: Gather initial patient information and complaints
2. **Symptom Analysis**: Ask targeted diagnostic questions based on the initial complaint
3. **Medical Recommendation**: Provide analysis, possible causes, and recommendations

The application integrates with Chutes AI for natural language processing and Supabase for data storage. It also includes PDF processing capabilities for analyzing laboratory results with ICD-11 integration.

## Features

- Three-stage medical consultation process
- Real-time chat interface with streaming responses
- Patient data extraction and storage
- Automatic chat history saving
- Responsive web interface with modern UI design
- Mobile-friendly layout with hamburger menu navigation
- Secure API integration with Chutes AI
- Database integration with Supabase
- Markdown support for rich text responses with HTML sanitization
- Gradient-based modern design with smooth animations
- Session management with auto-generated unique identifiers
- Error handling for API communication failures
- ICD-11 medical classification integration for enhanced diagnostic accuracy
- PDF processing for laboratory results analysis
- OCR support for scanned laboratory results
- AI-powered lab results summarization with medical context

## Technology Stack

### Backend
- **Python 3.x**
- **Flask** - Web framework
- **Chutes AI API** - AI model integration
- **Supabase** - Database storage
- **python-dotenv** - Environment variable management
- **ICD-11 API** - WHO International Classification of Diseases integration
- **PyPDF2** - PDF text extraction
- **pdfplumber** - Advanced PDF text extraction
- **pytesseract** - OCR for scanned documents
- **pdf2image** - PDF to image conversion for OCR

### Frontend
- **HTML5** - Semantic markup and structure
- **CSS3** - Modern styling with flexbox, gradients, and animations
- **JavaScript (ES6+)** - Modern JavaScript features for dynamic functionality
- **Marked.js** - Markdown parsing for rich text responses
- **DOMPurify** - HTML sanitization for security
- **Fetch API** - Modern HTTP client for API communication
- **TextDecoder API** - Handling streaming response data
- **CSS Grid & Flexbox** - Responsive layout design
- **CSS Media Queries** - Mobile-responsive design
- **CSS Animations** - Smooth transitions and effects

### Deployment
- **Vercel** - Hosting platform

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Node.js and npm (for development tools)
- Supabase account
- Chutes AI API token
- Tesseract OCR engine (for PDF processing)

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Medical-Chatbot-with-AI
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR:**
   - **Windows**: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

5. **Set up environment variables:**
   Create a `.env` file in the root directory with the following variables:
   ```env
   CHUTES_API_TOKEN=your_chutes_api_token
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

6. **Run the application:**
   ```bash
   python app.py
   ```

## Configuration

### Environment Variables

The application requires the following environment variables to be set in a `.env` file:

| Variable | Description | Required |
|----------|-------------|----------|
| `CHUTES_API_TOKEN` | API token for Chutes AI service | Yes |
| `SUPABASE_URL` | URL of your Supabase project | Yes |
| `SUPABASE_KEY` | API key for your Supabase project | Yes |
| `ICD11_CLIENT_ID` | Client ID for WHO ICD-11 API (optional, defaults to provided credentials) | No |
| `ICD11_CLIENT_SECRET` | Client secret for WHO ICD-11 API (optional, defaults to provided credentials) | No |

### Configuration Files

- [`config.py`](config.py) - Main configuration file
- [`prompts.py`](prompts.py) - System prompts for different stages
- [`vercel.json`](vercel.json) - Vercel deployment configuration

## Usage

1. Open the application in your web browser
2. Enter your name, age, gender, and initial complaint in the chat input
3. Follow the three-stage consultation process:
   - Stage 1: Answer 3 diagnostic questions
   - Stage 2: Receive medical analysis and recommendations
   - Stage 3: Ask follow-up questions (medical only)
4. View your chat history and patient data
5. Upload laboratory result PDFs for AI-powered analysis

### Patient Data Format

When starting a conversation, provide information in this format:
```
[Your Name], [Age], [Gender], [Initial Complaint]
Michael, 45 tahun, laki-laki, sakit kepala
```

### Laboratory Results Processing

1. After completing the consultation process, you can upload PDF laboratory results
2. The system will automatically extract text from the PDF using multiple methods:
   - pdfplumber for high-quality text extraction
   - PyPDF2 as fallback
   - OCR for scanned documents
3. The extracted text is cleaned to remove irrelevant information
4. Key laboratory values are extracted using pattern matching
5. ICD-11 context is retrieved for the identified medical terms
6. An AI-powered summary is generated with medical context and recommendations

## API Endpoints

### POST `/chat`

Process chat messages through the three-stage diagnostic system.

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
- Streaming text response with medical information
- Headers containing patient data and session ID

### POST `/save-chat`

Save chat history to the database.

**Request Body:**
```json
{
  "chatHistory": [
    {
      "timestamp": "ISO timestamp",
      "sender": "User|Bot",
      "message": "Message content"
    }
  ],
  "sessionId": "unique session identifier",
  "patientData": {
    "name": "Patient name",
    "age": "Patient age",
    "gender": "Patient gender",
    "keluhan_awal": "Initial complaint"
  }
}
```

**Response:**
```json
{
  "message": "Chat saved successfully"
}
```

### POST `/process-pdf`

Process laboratory result PDF files and generate AI-powered analysis.

**Request:**
- Multipart form data with PDF file
- `pdf`: The PDF file to process
- `session_id`: (optional) Session identifier

**Response:**
```json
{
  "summary": "AI-generated summary of lab results with medical context",
  "lab_values": {
    "Glukosa": {
      "value": "90",
      "unit": "mg/dL"
    }
  }
}
```

## Deployment

The application is configured for deployment on Vercel with the following setup:

### Vercel Configuration

The [`vercel.json`](vercel.json) file defines:
- Build configurations for Python and static files
- Route mappings for API endpoints
- Static file serving

### Deployment Steps

1. Push your code to a GitHub repository
2. Connect your repository to Vercel
3. Set environment variables in Vercel dashboard:
   - `CHUTES_API_TOKEN`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
4. Deploy the application

## ICD-11 Integration

The Medical Chatbot integrates with the WHO ICD-11 (International Classification of Diseases 11th Revision) API to enhance diagnostic accuracy. This integration provides:

- **Enhanced Medical Context**: During the analysis stage (Stage 2), the chatbot extracts relevant medical terms from the patient's initial complaint and queries the ICD-11 database for related information.
- **Improved Diagnostic Accuracy**: The ICD-11 context is provided to the AI model, helping it make more informed diagnostic recommendations.
- **Standardized Medical Terminology**: All medical terms are referenced against the WHO's official ICD-11 classification system.
- **Lab Results Context**: When processing laboratory results, ICD-11 context is retrieved for identified medical terms to enhance the analysis.

### How It Works

1. When a patient provides their initial complaint, the system extracts potential medical terms.
2. These terms are used to search the ICD-11 database through the WHO API.
3. Relevant ICD-11 entries are retrieved and formatted as context.
4. This context is injected into the system prompt for the analysis stage.
5. The AI model uses this additional medical information to provide more accurate analysis and recommendations.
6. For lab results, the same process is applied to identified medical parameters.

### Configuration

The ICD-11 integration uses OAuth 2.0 client credentials for authentication with the WHO API. The default credentials are provided in the application, but you can override them by setting the `ICD11_CLIENT_ID` and `ICD11_CLIENT_SECRET` environment variables.

## PDF Processing

The application includes advanced PDF processing capabilities for laboratory results:

### Text Extraction Methods

1. **pdfplumber**: Primary method for high-quality text extraction from digital PDFs
2. **PyPDF2**: Fallback method for compatibility with different PDF formats
3. **OCR (pytesseract)**: Final fallback for scanned documents or images in PDFs

### Text Processing

1. **Cleaning**: Removal of irrelevant headers, footers, and boilerplate text
2. **Value Extraction**: Pattern matching to identify laboratory values and units
3. **Context Analysis**: ICD-11 lookup for medical terms in the extracted text

### AI Analysis

1. **Summarization**: Generation of human-readable summaries of laboratory results
2. **Medical Context**: Integration of ICD-11 information for enhanced understanding
3. **Recommendations**: Suggestions for follow-up actions based on abnormal values

## Project Structure

```
Medical Chatbot with AI/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── prompts.py             # AI system prompts
├── utils.py               # Utility functions
├── icd11_client.py        # ICD-11 API client
├── pdf_processor.py       # PDF processing functions
├── index.html             # Main HTML interface with chat container
├── style.css              # Modern styling with responsive design
├── script.js              # Frontend JavaScript with streaming API communication
├── requirements.txt       # Python dependencies
├── vercel.json            # Vercel deployment config
├── .gitignore             # Git ignore rules
└── .env                   # Environment variables (not included in repo)
