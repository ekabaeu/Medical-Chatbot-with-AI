import firebase_admin
from firebase_admin import credentials, db
import os

def initialize_firebase():
    """
    Initialize Firebase Admin SDK with environment variables.
    This function safely handles multiple initialization attempts.
    """
    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        try:
            # Get Firebase credentials from environment variables
            # These will be set in Vercel environment variables
            firebase_config = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n') if os.getenv("FIREBASE_PRIVATE_KEY") else None,
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
            }
            
            # Check if all required environment variables are set
            required_vars = ["FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY_ID", "FIREBASE_PRIVATE_KEY", 
                           "FIREBASE_CLIENT_EMAIL", "FIREBASE_CLIENT_ID", "FIREBASE_CLIENT_CERT_URL"]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(f"Missing Firebase environment variables: {', '.join(missing_vars)}")
            
            # Initialize Firebase with credentials
            cred = credentials.Certificate(firebase_config)
            
            # Use the FIREBASE_DATABASE_URL environment variable, with a fallback to the default format
            database_url = os.getenv("FIREBASE_DATABASE_URL") or f'https://{os.getenv("FIREBASE_PROJECT_ID")}-default-rtdb.firebaseio.com/'
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            print("Firebase initialized successfully")
            print(f"Using database URL: {database_url}")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise e
    else:
        print("Firebase already initialized")
