import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config.settings import SCOPES, CREDENTIALS_FILE, TOKEN_FILE

def get_credentials():
    """
    Get valid user credentials from storage or initiate OAuth2 flow.
    
    Returns:
        Credentials: The obtained credentials.
    """
    creds = None
    
    # Load existing credentials if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Refresh or get new credentials if needed
    if not creds or not creds.valid:
        # if creds and creds.expired and creds.refresh_token:
        #     creds.refresh(Request())
        # else:
        #     flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        #     creds = flow.run_local_server(port=0)
        
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds 