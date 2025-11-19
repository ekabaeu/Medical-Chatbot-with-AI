# Configuration Documentation

This document provides detailed information about the configuration files used in the Medical Chatbot application.

## Table of Contents

- [Configuration Files Overview](#configuration-files-overview)
- [config.py](#configpy)
- [prompts.py](#promptspy)
- [vercel.json](#verceljson)
- [Environment Variables](#environment-variables)

## Configuration Files Overview

The Medical Chatbot application uses several configuration files to manage its settings, API integrations, and deployment configurations. These files are essential for the proper functioning of the application.

## config.py

The main configuration file that handles API keys, database connections, and application settings.

### Key Components

#### Chutes AI Configuration
```python
CHUTES_API_URL = "https://llm.chutes.ai/v1/chat/completions"
CHUTES_API_TOKEN = os.getenv("CHUTES_API_TOKEN")
MODEL_NAME = "deepseek-ai/DeepSeek-R1"
```

- `CHUTES_API_URL`: The endpoint for the Chutes AI API
- `CHUTES_API_TOKEN`: API token retrieved from environment variables
- `MODEL_NAME`: The specific AI model used for processing

#### Supabase Configuration
```python
def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    return supabase
```

- `get_supabase_client()`: Function that creates and returns a Supabase client instance
- Uses environment variables for secure credential management

#### Error Handling
The configuration includes error handling to ensure that required environment variables are set:
```python
if not CHUTES_API_TOKEN:
    raise ValueError("CHUTES_API_TOKEN tidak ditemukan. Harap buat file .env dan tambahkan variabel tersebut.")
```

## prompts.py

This file contains the system prompts that guide the AI's behavior in different stages of the consultation process.

### Three-Stage Prompt System

#### Stage 1: Information Collection
```python
system_prompt_task_1 = {
    "role": "system",
    "content": "Instructions for collecting initial patient information and asking 3 diagnostic questions"
}
```

#### Stage 2: Symptom Analysis
```python
system_prompt_task_2 = {
    "role": "system",
    "content": "Instructions for providing medical analysis based on collected information"
}
```

#### Stage 3: Natural Conversation
```python
system_prompt_task_3 = {
    "role": "system",
    "content": "Instructions for handling follow-up questions in a natural conversation style"
}
```

## vercel.json

The Vercel configuration file that defines how the application is built and deployed.

### Build Configuration
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    },
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ]
}
```

### Route Configuration
```json
{
  "routes": [
    {
      "src": "/chat",
      "dest": "app.py"
    }
  ]
}
```

## Environment Variables

The application requires several environment variables to be set for proper operation. These should be defined in a `.env` file in the project root.

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CHUTES_API_TOKEN` | API token for Chutes AI service | `sk-...` |
| `SUPABASE_URL` | URL of your Supabase project | `https://your-project.supabase.co` |
| `SUPABASE_KEY` | API key for your Supabase project | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

### Example .env File
```env
CHUTES_API_TOKEN=your_chutes_api_token_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_api_key_here