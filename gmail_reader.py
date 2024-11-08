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


import re

def extract_booking_info(email_body):
    """Extract booking information from a standardized email message."""
    try:
        # Split email into individual lines
        lines = email_body.strip().splitlines()

        # Extract fields based on line numbers
        first_name = "Not found"
        last_name = "Not found"
        
        # Extract name by analyzing the line containing "Mevrouw", "Meneer", or "Familie"
        name_match = re.search(r"(Mevrouw|Meneer|Familie)\s+([A-Za-z]+)\s+([\w\s]+)", lines[16])
        if name_match:
            first_name = name_match.group(2).strip()
            last_name = name_match.group(3).strip()

        # Email is expected on a specific line (line 23 based on example provided)
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", lines[23])
        email = email_match.group(0).strip() if email_match else "Not found"

        # Phone number is expected on line 22; directly take the entire line content
        phone = lines[22].strip()

        # Street address is expected on a specific line (line 19)
        street_address1 = lines[19].strip()

        # City and postal code are expected on a specific line (line 20)
        city_postal_match = re.search(r"(\d{4}\s?[A-Z]{2})\s+([A-Za-z\s]+)", lines[20])
        postal_code = city_postal_match.group(1).strip() if city_postal_match else "Not found"
        city = city_postal_match.group(2).strip() if city_postal_match else "Not found"


        # Guest count information is found on specific lines
        guest_adults_match = re.search(r"(\d+)\s+volwassenen", lines[17])
        guest_adults = int(guest_adults_match.group(1)) if guest_adults_match else 0

        guest_children_match = re.search(r"(\d+)\s+kinderen", lines[18])
        guest_children = int(guest_children_match.group(1)) if guest_children_match else 0

        guest_infants_match = re.search(r"(\d+)\s+baby'?s", lines[18])
        guest_infants = int(guest_infants_match.group(1)) if guest_infants_match else 0

        # Guest message is expected after line 24 and before structured content
        guest_message_lines = []
        for line in lines[25:]:
            if re.match(r"^\|", line):  # Stop at the price section or any structured line
                break
            guest_message_lines.append(line.strip())
        guest_message = " ".join(guest_message_lines).strip()

        # Arrival and departure dates are expected on a specific line (line 10)
        dates_match = re.search(r"Periode:\s+\w+\s(\d{2}-\d{2}-\d{4})\s+tot\s+\w+\s(\d{2}-\d{2}-\d{4})", lines[10])
        arrival = dates_match.group(1).strip() if dates_match else "Not found"
        departure = dates_match.group(2).strip() if dates_match else "Not found"

        # Regular price is found in the specific line containing "Reguliere prijs"
        regular_price = 0.0
        for line in lines:
            if "Reguliere prijs" in line:
                price_match = re.search(r"Euro\s([\d.,]+)", line)
                if price_match:
                    regular_price = float(price_match.group(1).replace('.', '').replace(',', '.'))
                break

        # Organize extracted data into a dictionary
        booking_info = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "street_address1": street_address1,
            "city": city,
            "postal_code": postal_code,
            "guest_adults": guest_adults,
            "guest_children": guest_children,
            "guest_infants": guest_infants,
            "guest_message": guest_message,
            "arrival": arrival,
            "departure": departure,
            "regular_price": regular_price
        }

        return booking_info

    except Exception as e:
        print("Error extracting booking info:", e)
        return None

if __name__ == "__main__":
    # Sample email body text for testing
    email_body = """
    Beste J.W.Louwerens,

    Er is een nieuwe boekingsaanvraag binnengekomen bij de Boekingsassistent.

    Accommodatie: de Dwergstern

    Periode: maandag 16-06-2025 tot zondag 22-06-2025

    Boekingsnummer: 2025-1015
    Validatiecode: VLbzm

    Deelnemers:
    - 2 volwassenen
    - 2 kinderen
    - 1 baby's

    Contactgegevens klant:
    Familie Henk de Tester
    Straat 3
    1234 BQ Henkland

    +31612345678
    johndoe@gmail.com
    __

    Onderwerp van bericht hallo dit is de body van het bericht wat een gast kan typen. danku jahor. |-------------------------------------------------------------------- |Concept prijsberekening door het systeem o.b.v. prijzentabel en accommodatie-gegevens: | - Vakantie van maandag 16-06-2025 tot zondag 22-06-2025 voor 5 personen | |Reguliere prijs (7d6n) is Euro 1425.00 | - Vertrekdag zondag 22-06-2025 is geen wisseldag (maandag 23-06-2025 gebruikt).Tip: een andere vertrekdag kan een betere huurprijs geven. | - Reguliere prijs per week is Euro 1425 | |Toeristenbelasting Euro 57.90 | - Toeristenbelasting 2025 is Euro 1.93 p.p.p.n. (5p, 6n) | |Eindschoonmaak Euro 95.00 | - Eindschoonmaak verplicht | |Linnengoed | - zelf meenemen of lokaal/op `t eiland huren | - Huur bed-, bad- en keukenlinnen ! | |Borg | - geen borg | |TOTAAL (exclusief borg) is Euro 1577.90 | |Voor zover ons bekend zijn de gegevens in dit venster correct.Maar U kunt geen rechten aan deze informatie ontlenen. Fouten graag rapporteren per email aan de webmaster. Alvast bedankt.
    __

    Deze aanvraag verwerken kan via https://www.Boekingsassistent.net
    """
    
    booking_info = extract_booking_info(email_body)
    print(booking_info)


if __name__ == "__main__":
    service = initialize_gmail_api()
    emails = get_matching_emails(service)
    print("Extracted email data:", emails)