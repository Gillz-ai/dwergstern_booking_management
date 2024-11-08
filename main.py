# main.py

from gmail_reader import initialize_gmail_api, get_matching_emails
from lodgify_api import create_reservation

def main():
    # Initialize Gmail API and retrieve emails
    service = initialize_gmail_api()
    email_data = get_matching_emails(service)
    
    for data in email_data:
        create_reservation(data)  # Send extracted data to Lodgify

if __name__ == "__main__":
    main()
