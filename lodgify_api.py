# lodgify_api.py

import requests

# Lodgify API credentials
LODGIFY_API_KEY = "A9L4LWkBCsbmi3THF7Mmld7ElxOKlvnIugZbil6KaUnOMo/s4CG+WeiIEbLvT/QS"
LODGIFY_URL = "https://api.lodgify.com/v1/reservation/booking"

def create_reservation(data):
    """Post a new reservation to Lodgify using extracted email data."""
    headers = {
        "X-ApiKey": LODGIFY_API_KEY,
        "accept": "application/json",
        "content-type": "application/*+json"
    }
    
    # Construct payload with variable data
    payload = {
        "guest": {
            "guest_name": {
                "first_name": data["first_name"],
                "last_name": data["last_name"]
            },
            "email": data["email"],
            "phone": data["phone"],
            "street_address1": data["street_address1"],
            "city": data["city"],
            "country_code": data["country_code"],
            "postal_code": data["postal_code"],
        },
        "rooms": [
            {
                "guest_breakdown": {
                    "adults": data["guest_adults"],
                    "children": data["guest_children"],
                    "infants": data["guest_infants"],
                },
                "room_type_id": 685974
            }
        ],
        "messages": [
            {
                "subject": "",
                "message": data["guest_message"],
                "type": "Renter"
            }
        ],
        "bookability": "BookingRequest",
        "total": data["total_price"],
        "currency_code": "EUR",
        "arrival": data["arrival"],
        "departure": data["departure"],
        "property_id": 619075,
        "status": "Tentative"
    }

    # Send the POST request with JSON payload
    response = requests.post(LODGIFY_URL, json=payload, headers=headers)

    if response.status_code == 201:
        print("Reservation created successfully!")
    else:
        print(f"Failed to create reservation: Status Code {response.status_code}")
        print("Response Text:", response.text)

if __name__ == "__main__":
    # Example data for testing
    test_data = {
        "first_name": "Test",
        "last_name": "Zoveel",
        "email": "john@doe1234567.com",
        "phone": "0612345678",
        "street_address1": "asdfjkl 12",
        "city": "Den Haag",
        "country_code": "NL",
        "postal_code": "2585JE",
        "guest_adults": 1,
        "guest_children": 1,
        "guest_infants": 1,
        "guest_message": 'Ik zou het heel leuk vinden met mijn familie tijd te spenderen in uw\r\nhuisje!\r\n-------------------------------------------------------------------------------\r\n\r\n--------------------------------------------------------------------\r\nConcept prijsberekening door het systeem o.b.v. prijzentabel en\r\naccommodatie-gegevens:\r\n - Vakantie van vrijdag 15-11-2024 tot maandag 18-11-2024 voor 5 personen\r\n\r\nReguliere prijs (4d3n) is Euro 735.00\r\n - Reguliere prijs per weekend is Euro 735\r\n\r\nToeristenbelasting Euro 28.95\r\n - Toeristenbelasting 2024 is Euro 1.93 p.p.p.n. (5p, 3n)\r\n\r\nEindschoonmaak Euro 95.00\r\n - Eindschoonmaak verplicht\r\n\r\nLinnengoed\r\n - zelf meenemen of lokaal/op `t eiland huren\r\n - Huur bed-, bad- en keukenlinnen !\r\n\r\nBorg\r\n - geen borg\r\n\r\nTOTAAL (exclusief borg) is Euro 858.95\r\n\r\nVoor zover ons bekend zijn de gegevens in dit venster correct.Maar U kunt\r\ngeen rechten aan deze informatie ontlenen. Fouten graag rapporteren per\r\nemail aan de webmaster. Alvast bedankt.',
        "total_price": 1200.00,
        "arrival": '15-11-2024',
        "departure": '18-11-2024',
        }
    create_reservation(test_data)
