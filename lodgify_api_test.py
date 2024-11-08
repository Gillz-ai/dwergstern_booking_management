import requests

url = "https://api.lodgify.com/v1/properties"

headers = {
    "accept": "application/json",
    "X-ApiKey": "A9L4LWkBCsbmi3THF7Mmld7ElxOKlvnIugZbil6KaUnOMo/s4CG+WeiIEbLvT/QS"
}

response = requests.get(url, headers=headers)

print(response.text)