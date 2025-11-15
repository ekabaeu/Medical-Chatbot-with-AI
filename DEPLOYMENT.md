# Deployment Guide

## Deploying to Vercel

This guide will walk you through deploying the Medical Chatbot application to Vercel for permanent hosting.

### Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. A GitHub account
3. Your Chutes AI API token

### Step-by-Step Deployment

#### 1. Fork the Repository

1. Go to your GitHub account
2. Fork this repository to your account

#### 2. Configure Environment Variables

Before deploying, you'll need to set up environment variables in Vercel:

1. In your Vercel dashboard, select your project
2. Go to Settings > Environment Variables
3. Add the following variable:
   - Name: `CHUTES_API_TOKEN`
   - Value: Your actual Chutes AI API token

#### 3. Deploy via Vercel Dashboard

1. Go to your Vercel dashboard
2. Click "New Project"
3. Import your forked repository
4. Configure the project:
   - Framework Preset: `Other`
   - Root Directory: Leave as default
   - Build Command: Leave as default (Vercel will auto-detect)
   - Output Directory: Leave as default
5. Click "Deploy"

#### 4. Alternative: Deploy via Vercel CLI

If you prefer using the command line:

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Log in to your Vercel account:
   ```bash
   vercel login
   ```

3. Deploy the project:
   ```bash
   vercel
   ```

4. Follow the prompts to configure your project

### Configuration Files

This project includes several configuration files for Vercel deployment:

- `vercel.json`: Main configuration for Vercel deployment
- `requirements.txt`: Python dependencies
- `static.json`: Configuration for serving static files
- `.env.example`: Example environment variables

### Important Notes

1. **API Token Security**: Never commit your actual API tokens to the repository. Always use environment variables.

2. **File Storage**: The application saves chat logs to CSV files. In a production environment on Vercel, these files are stored in the serverless function's temporary file system and may be lost when the function scales down. For persistent storage, consider using a database or external storage service.

3. **CORS**: The application is configured to handle CORS properly for frontend-backend communication.

4. **Frontend-Backend Integration**: The frontend automatically uses the same origin as the backend when deployed, so no manual configuration is needed for the API endpoints.

### Troubleshooting

#### Common Issues

1. **Deployment Fails**: Check the build logs in your Vercel dashboard for specific error messages.

2. **API Calls Failing**: Ensure your `CHUTES_API_TOKEN` environment variable is correctly set in Vercel.

3. **CORS Errors**: The application should already be configured correctly, but if you encounter issues, check that the CORS middleware is properly configured in `app.py`.

#### Checking Logs

You can view detailed logs for your deployment in the Vercel dashboard:
1. Go to your project in the Vercel dashboard
2. Click on the deployment you want to inspect
3. View the logs for build and runtime information

### Updating Your Deployment

To update your deployed application after making changes:

1. Push your changes to your GitHub repository
2. Vercel will automatically redeploy your application
3. Or manually trigger a new deployment from the Vercel dashboard

### Custom Domain (Optional)

To use a custom domain:

1. In your Vercel dashboard, go to your project settings
2. Navigate to the "Domains" section
3. Add your custom domain
4. Follow the instructions to configure DNS records with your domain provider