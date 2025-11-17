# Deployment Guide with Firebase Integration

## Prerequisites

1. Ensure you have the latest version of the code with Firebase integration
2. Have a Firebase account (free tier is sufficient)
3. Install the Vercel CLI: `npm install -g vercel`

## Firebase Setup

1. Create a Firebase account at https://firebase.google.com/
2. Create a new project in the Firebase Console
3. In the Firebase Console, go to Project Settings > Service Accounts
4. Generate a new private key and download the JSON file
5. Rename the downloaded file to `serviceAccountKey.json` and place it in your project root directory

## Environment Variables Setup

You need to set the following environment variables in your Vercel project:

1. In your Vercel dashboard, go to your project settings
2. Navigate to the "Environment Variables" section
3. Add the following variables:

```
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY=your_private_key (replace \n with actual newlines)
FIREBASE_CLIENT_EMAIL=your_client_email
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_CLIENT_CERT_URL=your_client_cert_url
CHUTES_API_TOKEN=your_chutes_api_token
```

To get these values:
1. Open your `serviceAccountKey.json` file
2. Extract the corresponding values from the JSON file
3. For the `FIREBASE_PRIVATE_KEY`, make sure to replace literal `\n` characters with actual newlines when setting the environment variable

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
   - Patient data appears in your Firebase Realtime Database under `patients`
   - Chat history appears in your Firebase Realtime Database under `chat_logs`

## Troubleshooting

If you encounter issues:

1. Check the Vercel function logs for any error messages
2. Verify all environment variables are correctly set
3. Ensure your Firebase project has Realtime Database enabled
4. Check that your service account has the necessary permissions

## Local Development

For local development, create a `.env` file in your project root with the same variables as above. Make sure to add `serviceAccountKey.json` to your `.gitignore` file to avoid committing it to version control.