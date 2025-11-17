# Deployment Guide with Supabase Integration

## Prerequisites

1. Ensure you have the latest version of the code with Supabase integration
2. Have a Supabase account (free tier is sufficient)
3. Install the Vercel CLI: `npm install -g vercel`

## Supabase Setup

1. Create a Supabase account at https://supabase.com/
2. Create a new project in the Supabase Console
3. In the Supabase Console, go to Project Settings > API
4. Note down your Project URL and anon/public API key

## Database Schema Setup

In your Supabase SQL editor, run the following SQL commands to create the required tables:

```sql
-- Create patients table
CREATE TABLE patients (
  id SERIAL PRIMARY KEY,
  id_pasien TEXT UNIQUE,
  nama TEXT,
  umur INTEGER,
  gender TEXT,
  keluhan_awal TEXT,
  session_id TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create chat_logs table
CREATE TABLE chat_logs (
  id SERIAL PRIMARY KEY,
  session_id TEXT,
  chat_history JSONB,
  patient_data JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Environment Variables Setup

You need to set the following environment variables in your Vercel project:

1. In your Vercel dashboard, go to your project settings
2. Navigate to the "Environment Variables" section
3. Add the following variables:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
CHUTES_API_TOKEN=your_chutes_api_token
```

To get these values:
1. Project URL: From your Supabase project settings > API > Project URL
2. anon/public API key: From your Supabase project settings > API > Project API keys
3. CHUTES_API_TOKEN: Your existing Chutes AI API token

## Deployment Steps

1. Commit all your changes to git
2. Run `vercel` in your project directory
3. Follow the prompts to deploy your project
4. When asked about environment variables, you can either:
   - Set them during the deployment process
   - Set them in the Vercel dashboard after deployment

## Testing the Deployment

1. After deployment, visit your deployed URL
2. Start a new chat session
3. Provide patient information in your first message
4. Continue the conversation with medical questions
5. End the session and check if:
   - Patient data appears in your Supabase `patients` table
   - Chat history appears in your Supabase `chat_logs` table

## Troubleshooting

If you encounter issues:

1. Check the Vercel function logs for any error messages
2. Verify all environment variables are correctly set
3. Ensure your Supabase project has the required tables with correct schema
4. Check that your Supabase API keys have the necessary permissions

## Local Development

For local development, create a `.env` file in your project root with the same variables as above.