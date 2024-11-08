import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import email
import re 


# Define scopes and file paths
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"

def initialize_gmail_api():
    """Initializes the Gmail API service, using token reuse to manage authentication."""
    creds = None
    
    # Load credentials from token.json if it exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Check if credentials are invalid or expired, and refresh or prompt login as necessary
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=8080)
        
        # Save the updated credentials back to token.json for reuse
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    
    # Initialize the Gmail API service
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return None
        print("Labels:")
        for label in labels:
            print(label["name"])

        return service

    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def get_matching_emails(service):
    """Fetch unread emails that match specific criteria (subject, sender, etc.)."""
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='from:gilleslouwerens@gmail.com subject:"Boekingsassistent.net: Nieuwe boekingsaanvraag" newer_than:2d').execute()
    messages = results.get('messages', [])
    email_data = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        email_body = get_email_body(msg_data['payload'])
        
        # Extract details based on regex patterns
        if email_body:
            booking_info = extract_booking_info(email_body)
            if booking_info:
                email_data.append(booking_info)
    
    return email_data

def get_email_body(payload):
    """Extract the email body from the message payload."""
    if 'parts' in payload:
        # If the email has multiple parts, iterate through them
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':  # Adjust if you prefer 'text/html'
                body_data = part['body'].get('data')
                if body_data:
                    return base64.urlsafe_b64decode(body_data).decode('utf-8')
    else:
        # If there's no 'parts' key, try to get the data from 'body'
        body_data = payload['body'].get('data')
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode('utf-8')
    
    # Return None if no suitable body content was found
    return None


def extract_booking_info(email_body):
    """Extract relevant booking information using regex patterns."""
    try:
        # Customize these regex patterns based on the email content format
        Boekingsnummer = re.search(r"Boekingsnummer: (.*)", email_body).group(1)
        Validatiecode = re.search(r"Validatiecode: (.*)", email_body).group(1)
        Periode = re.search(r"Periode: (.*)", email_body).group(1)
        
        return {
            "Boekingsnummer": Boekingsnummer,
            "Validatiecode": Validatiecode,
            "Periode": Periode
        }
    except AttributeError:
        return None  # Return None if regex doesn't match

if __name__ == "__main__":
    service = initialize_gmail_api()
    emails = get_matching_emails(service)
    print("Extracted email data:", emails)