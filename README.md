# Medical Chatbot with AI

A Flask-based medical chatbot application that uses AI to assist patients with initial medical consultations. The application features a three-stage diagnostic process that collects patient information, analyzes symptoms, and provides medical recommendations.

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

The application integrates with Chutes AI for natural language processing and Supabase for data storage.

## Features

- Three-stage medical consultation process
- Real-time chat interface with streaming responses
- Patient data extraction and storage
- Automatic chat history saving
- Responsive web interface
- Secure API integration with Chutes AI
- Database integration with Supabase
- Markdown support for rich text responses

## Technology Stack

### Backend
- **Python 3.x**
- **Flask** - Web framework
- **Chutes AI API** - AI model integration
- **Supabase** - Database storage
- **python-dotenv** - Environment variable management

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript (ES6+)**
- **Marked.js** - Markdown parsing
- **DOMPurify** - HTML sanitization

### Deployment
- **Vercel** - Hosting platform

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Node.js and npm (for development tools)
- Supabase account
- Chutes AI API token

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

4. **Set up environment variables:**
   Create a `.env` file in the root directory with the following variables:
   ```env
   CHUTES_API_TOKEN=your_chutes_api_token
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

5. **Run the application:**
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

### Patient Data Format

When starting a conversation, provide information in this format:
```
[Your Name] [Age] [Gender] [Initial Complaint]
Example: John 25 male I have a headache and fever
```

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

## Project Structure

```
Medical Chatbot with AI/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── prompts.py             # AI system prompts
├── utils.py               # Utility functions
├── index.html             # Main HTML interface
├── style.css              # Styling
├── script.js              # Frontend JavaScript
├── requirements.txt       # Python dependencies
├── vercel.json            # Vercel deployment config
├── .gitignore             # Git ignore rules
└── .env                   # Environment variables (not included in repo)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.