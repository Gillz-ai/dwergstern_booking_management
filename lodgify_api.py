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
            "street_address2": data["street_address2"],
            "city": data["city"],
            "country_code": data["country_code"],
            "postal_code": data["postal_code"],
            "state": data["state"]
        },
        "rooms": [
            {
                "guest_breakdown": {
                    "adults": data["guest_adults"],
                    "children": data["guest_children"],
                    "infants": data["guest_infants"],
                    "pets": data["guest_pets"]
                },
                "room_type_id": 685974
            }
        ],
        "messages": [
            {
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
        "first_name": "lul",
        "last_name": "lullo",
        "email": "gilleslouwerens@gmail.com",
        "phone": "0612345678",
        "street_address1": "asdfjkl 12",
        "street_address2": "asdflkj",
        "city": "Den Haag",
        "country_code": "NL",
        "postal_code": "2585JE",
        "state": "Zuid-Holland",
        "guest_adults": 1,
        "guest_children": 1,
        "guest_infants": 1,
        "guest_pets": 1,
        "guest_message": "dit huis graag",
        "total_price": 1200,
        "arrival": "2024-12-15",
        "departure": "2025-12-18",
        }
    create_reservation(test_data)
