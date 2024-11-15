import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
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
    """Extract booking information from a flexible email format using keywords and patterns."""
    
    try:
        # Split email into individual lines
        lines = email_body.strip().splitlines()

        # Extract fields based on keywords and patterns
        # Extract first name and last name (only if on the same line as "Boeker:")
        name_match = re.search(r"Boeker:\s*(?:Mw\.|Dhr\.)?\s*([A-Za-z]+)\s+([A-Za-z]*)\s*$", email_body, re.MULTILINE)
        first_name = name_match.group(1).strip() if name_match else "Not found"
        last_name = name_match.group(2).strip() if name_match and name_match.group(2) else "Not found"
        
        # Extract email (line containing "email:")
        email_match = re.search(r"email:\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", email_body)
        email = email_match.group(1).strip() if email_match else "Not found"

        # Extract phone number (line containing "telefoon:")
        phone_match = re.search(r"telefoon:\s*([\+0-9\s-]+)", email_body)
        phone = phone_match.group(1).strip() if phone_match else "Not found"

        # Extract street address (assumes the address follows "Boeker:" line)
        street_address_match = re.search(r"Boeker:.*?\n\s*([A-Za-z\s]+ \d+)", email_body, re.DOTALL)
        street_address1 = street_address_match.group(1).strip() if street_address_match else "Not found"

        # Extract postal code and city from the line following the street address line
        postal_city_match = re.search(r"\n\s*(\d{4}\s?[A-Z]{2})\s+([A-Za-z\s]+)\s*\n", email_body)
        postal_code = postal_city_match.group(1).strip() if postal_city_match else "Not found"
        city = postal_city_match.group(2).strip().split()[0] if postal_city_match else "Not found"

        # Extract country code (based on presence of "nl" or similar in the address section)
        country_code = "NL" if "nl" in email_body.lower() else \
                   "DE" if "de" in email_body.lower() else \
                   "UK" if "uk" in email_body.lower() else \
                   "BE" if "be" in email_body.lower() else "Other"

        # Extract guest counts (based on keywords "Personen", "Kinderen", and "Babies")
        guest_adults_match = re.search(r"Personen \(12 en ouder\):\s+(\d+)", email_body)
        guest_adults = int(guest_adults_match.group(1)) if guest_adults_match else 0

        guest_children_match = re.search(r"Kinderen \(4-12 jaar\):\s+(\d+)", email_body)
        guest_children = int(guest_children_match.group(1)) if guest_children_match else 0

        guest_infants_match = re.search(r"Babies \(tot 4 jaar\):\s+(\d+)", email_body)
        guest_infants = int(guest_infants_match.group(1)) if guest_infants_match else 0

        # Extract guest message: everything below "Bericht:" up to the end of the email
        message_match = re.search(r"Bericht:\s*[-\s]*\n(.*)", email_body, re.DOTALL)
        guest_message = message_match.group(1).strip() if message_match else "Not found"

        # Extract arrival and departure dates (line containing "Periode:")
        dates_match = re.search(r"Periode:\s+\w+\s(\d{2}-\d{2}-\d{4})\s+tot\s+\w+\s(\d{2}-\d{2}-\d{4})", email_body)
        if dates_match:
            arrival = datetime.strptime(dates_match.group(1).strip(), "%d-%m-%Y").strftime("%Y-%m-%d")
            departure = datetime.strptime(dates_match.group(2).strip(), "%d-%m-%Y").strftime("%Y-%m-%d")
        else:
            arrival = "Not found"
            departure = "Not found"

        # Extract regular price (line containing "Reguliere prijs") and handle thousands separator correctly
        regular_price_match = re.search(r"Reguliere prijs.*?Euro\s([\d.,]+)", email_body)
        regular_price = float(regular_price_match.group(1).replace(',', '')) if regular_price_match else 0.0


        # Organize extracted data into a dictionary
        booking_info = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "street_address1": street_address1,
            "city": city,
            "postal_code": postal_code,
            "country_code": country_code,
            "guest_adults": guest_adults,
            "guest_children": guest_children,
            "guest_infants": guest_infants,
            "guest_message": guest_message,
            "arrival": arrival,
            "departure": departure,
            "total_price": regular_price
        }

        return booking_info

    except Exception as e:
        print("Error extracting booking info:", e)
        return None

if __name__ == "__main__":
    # Sample email body text for testing
    email_body = """
    Vanaf op-Schiermonnikoog.nl verstuurd
    Door:                              Els (info@op-schiermonnikoog.nl)
    Aan:                               info@dwergstern.nl
    Betreft:                           test aanvraag
    Inzake Vakantiehuis:    de Dwergstern voor de periode vrijdag 15-11-2024 tot maandag 18-11-2024

    -------------------------------------------------------------------------------

    DIT IS EEN RESERVERING

    Accommodatie:                      DE DWERGSTERN
    Periode:                           vrijdag 15-11-2024 tot maandag 18-11-2024


    Klantgegevens:
    -------------------------------------------------------------------------------
    Boeker:                            Mw. Els
                                       Rembrandtstraat 15
                                       7204 BW Zutphen
                                       nl

    telefoon:                          0612345678
    email:                             info@op-schiermonnikoog.nl

    Personen (12 en ouder):            2
    Kinderen (4-12 jaar):              2
    Babies (tot 4 jaar):               1



    -------------------------------------------------------------------------------


    Bericht:
    -------------------------------------------------------------------------------
    test aanvraag 
    Hier volgt nog meer informatie van de gast. 
    Bedankt en vriendelijke groeten.
    -------------------------------------------------------------------------------

    --------------------------------------------------------------------
    Concept prijsberekening door het systeem o.b.v. prijzentabel en accommodatie-gegevens:
     - Vakantie van vrijdag 15-11-2024 tot maandag 18-11-2024 voor 5 personen

    Reguliere prijs (4d3n) is Euro 735.00
     - Reguliere prijs per weekend is Euro 735

    Toeristenbelasting Euro 28.95
     - Toeristenbelasting 2024 is Euro 1.93 p.p.p.n. (5p, 3n)

    Eindschoonmaak Euro 95.00
     - Eindschoonmaak verplicht

    Linnengoed
     - zelf meenemen of lokaal/op `t eiland huren
     - Huur bed-, bad- en keukenlinnen !

    Borg
     - geen borg

    TOTAAL (exclusief borg) is Euro 858.95

    Voor zover ons bekend zijn de gegevens in dit venster correct.Maar U kunt geen rechten aan deze informatie ontlenen. Fouten graag rapporteren per email aan de webmaster. Alvast bedankt.
    """
    
    booking_info = extract_booking_info(email_body)
    print(booking_info)


if __name__ == "__main__":
    service = initialize_gmail_api()
    emails = get_matching_emails(service)
    print("Extracted email data:", emails)