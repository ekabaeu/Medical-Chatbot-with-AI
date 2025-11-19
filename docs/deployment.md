# Deployment Documentation

This document provides detailed information about deploying the Medical Chatbot application to production environments.

## Table of Contents

- [Deployment Architecture](#deployment-architecture)
- [Vercel Deployment](#vercel-deployment)
- [Environment Configuration](#environment-configuration)
- [Build Process](#build-process)
- [Routing Configuration](#routing-configuration)
- [Database Setup](#database-setup)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## Deployment Architecture

The Medical Chatbot application is designed for deployment on Vercel, leveraging its serverless functions for the Python backend and static file hosting for frontend assets.

### Architecture Components

1. **Frontend**: Static HTML, CSS, and JavaScript files
2. **Backend**: Python Flask application running as serverless functions
3. **Database**: Supabase PostgreSQL database
4. **AI Service**: Chutes AI API integration
5. **CDN**: Vercel's global CDN for content delivery

### Data Flow in Production

1. User accesses application through Vercel CDN
2. Static files served directly from CDN
3. API requests routed to serverless functions
4. Serverless functions communicate with external services
5. Data stored and retrieved from Supabase database

## Vercel Deployment

The application is configured for deployment on Vercel using the `vercel.json` configuration file.

### Deployment Configuration

#### Build Settings
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
    },
    {
      "src": "style.css",
      "use": "@vercel/static"
    },
    {
      "src": "script.js",
      "use": "@vercel/static"
    }
  ]
}
```

#### Routing Configuration
```json
{
  "routes": [
    {
      "src": "/chat",
      "dest": "app.py"
    },
    {
      "src": "/save-chat",
      "dest": "app.py"
    },
    {
      "src": "/(index.html|style.css|script.js)",
      "dest": "/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### Deployment Steps

1. **Repository Setup**
   - Push code to GitHub/GitLab/Bitbucket repository
   - Ensure all required files are included
   - Verify `.gitignore` is properly configured

2. **Vercel Project Creation**
   - Log in to Vercel dashboard
   - Create new project from Git repository
   - Select appropriate repository

3. **Environment Variables Configuration**
   - Navigate to project settings
   - Go to "Environment Variables" section
   - Add required variables:
     - `CHUTES_API_TOKEN`
     - `SUPABASE_URL`
     - `SUPABASE_KEY`

4. **Deployment Trigger**
   - Push to main branch to trigger automatic deployment
   - Or manually trigger deployment from Vercel dashboard
   - Monitor deployment logs for any issues

5. **Domain Configuration**
   - Use default Vercel domain or add custom domain
   - Configure DNS settings if using custom domain
   - Enable SSL certificate (automatically provided by Vercel)

## Environment Configuration

### Required Environment Variables

| Variable | Description | Security Level |
|----------|-------------|----------------|
| `CHUTES_API_TOKEN` | API token for Chutes AI service | High |
| `SUPABASE_URL` | URL of your Supabase project | Medium |
| `SUPABASE_KEY` | API key for your Supabase project | High |

### Environment Variable Management

1. **Development**: Use `.env` file (gitignored)
2. **Production**: Set through Vercel dashboard
3. **Security**: Never commit secrets to repository

### Configuration Validation

The application includes validation to ensure required environment variables are set:
```python
if not CHUTES_API_TOKEN:
    raise ValueError("CHUTES_API_TOKEN tidak ditemukan. Harap buat file .env dan tambahkan variabel tersebut.")
```

## Build Process

### Python Backend Build

Vercel uses the `@vercel/python` builder for the Flask application:

1. Installs Python dependencies from `requirements.txt`
2. Sets up Python runtime environment
3. Configures serverless function handlers
4. Optimizes for cold start performance

### Static Asset Build

Frontend assets are served as static files:

1. HTML files served directly
2. CSS files served with proper MIME types
3. JavaScript files served with proper MIME types
4. All assets cached through Vercel CDN

### Build Optimization

- Automatic minification of static assets
- Global CDN distribution
- HTTP/2 support
- Automatic compression (gzip/Brotli)

## Routing Configuration

### API Routes

```json
{
  "src": "/chat",
  "dest": "app.py"
}
```

- Routes `/chat` requests to Flask application
- Handles POST requests for chat processing
- Supports streaming responses

```json
{
  "src": "/save-chat",
  "dest": "app.py"
}
```

- Routes `/save-chat` requests to Flask application
- Handles POST requests for chat history saving

### Static File Routes

```json
{
  "src": "/(index.html|style.css|script.js)",
  "dest": "/$1"
}
```

- Direct routing for specific static files
- Maintains original file paths

### Fallback Route

```json
{
  "src": "/(.*)",
  "dest": "/index.html"
}
```

- Catch-all route for SPA functionality
- Ensures all routes serve `index.html`
- Enables client-side routing

## Database Setup

### Supabase Configuration

1. **Project Creation**
   - Create new project in Supabase dashboard
   - Select appropriate region
   - Configure database settings

2. **Database Schema**
   - `patients` table for patient information
   - `chat_logs` table for chat history
   - Proper indexing for performance

3. **Authentication**
   - Generate service role key for backend access
   - Configure Row Level Security (RLS) if needed
   - Set up appropriate permissions

### Required Tables

#### patients Table
```sql
CREATE TABLE patients (
  id_pasien TEXT PRIMARY KEY,
  nama TEXT,
  umur INTEGER,
  gender TEXT,
  keluhan_awal TEXT,
  session_id TEXT
);
```

#### chat_logs Table
```sql
CREATE TABLE chat_logs (
  session_id TEXT PRIMARY KEY,
  chat_history JSONB,
  patient_data JSONB
);
```

## Monitoring and Maintenance

### Performance Monitoring

1. **Vercel Analytics**
   - Built-in performance metrics
   - Request duration tracking
   - Error rate monitoring

2. **Custom Logging**
   - Application-level logging in Python functions
   - Error tracking and reporting
   - Performance metrics collection

### Maintenance Tasks

1. **Dependency Updates**
   - Regular review of `requirements.txt`
   - Security updates for Python packages
   - Compatibility testing after updates

2. **Database Maintenance**
   - Regular backups of Supabase database
   - Performance optimization queries
   - Storage cleanup for old data

3. **Security Updates**
   - Regular review of environment variables
   - API token rotation
   - Security audit of dependencies

### Scaling Considerations

1. **Vercel Serverless Functions**
   - Automatic scaling based on demand
   - Cold start optimization
   - Request concurrency handling

2. **Database Scaling**
   - Supabase automatic scaling
   - Connection pooling
   - Query optimization

3. **CDN Performance**
   - Global edge network
   - Asset caching strategies
   - Bandwidth optimization