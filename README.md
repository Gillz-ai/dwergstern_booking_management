## Files

- `gmail_reader.py`: Contains functions to initialize the Gmail API, fetch matching emails, extract email body, and extract booking information.
- `lodgify_api.py`: Contains functions to create reservations in the Lodgify API.
- `main.py`: Main script to initialize the Gmail API, retrieve emails, and create reservations.
- `lodgify_api_test.py`: Script to test the Lodgify API.
- `requirements.txt`: Lists the dependencies required for the project.
- `testing.ipynb`: Jupyter notebook for testing and development.

## Setup

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up your Gmail API credentials:
    - Follow the instructions at [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python) to create `credentials.json`.
    - Place the `credentials.json` file in the root directory of the project.

## Usage

1. Run the main script:
    ```sh
    python main.py
    ```

2. The script will initialize the Gmail API, fetch unread emails matching specific criteria, extract booking information, and create reservations in the Lodgify API.

## Functions

### `gmail_reader.py`

- `initialize_gmail_api()`: Initializes the Gmail API service, using token reuse to manage authentication.
- `get_matching_emails(service)`: Fetches unread emails that match specific criteria (subject, sender, etc.).
- `get_email_body(payload)`: Extracts the email body from the message payload.
- `extract_booking_info(email_body)`: Extracts booking information from a flexible email format using keywords and patterns.

### `lodgify_api.py`

- `create_reservation(data)`: Posts a new reservation to Lodgify using extracted email data.

## License

This project is licensed under the MIT License.