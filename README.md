## Overview
This Python script utilizes the Gmail API to fetch emails based on a specified time range (default is 1 hour) and saves them to a CSV file. It retrieves email metadata such as ID, subject, sender, recipient, date, received timestamp, body, and labels.

## Requirements
1. Python 3.x
3. Required Python packages:
	- google-auth
	- google-auth-oauthlib
	- google-api-python-client
	- pytz
	- dateutil
	- base64 (part of Python standard library)

Install with pip:
pip install google-auth google-auth-oauthlib google-api-python-client pytz python-dateutil


## Setup
1. Install Dependencies:
```
   pip install google-auth google-auth-oauthlib google-api-python-client pytz python-dateutil
```
   or:
```
   pip install -r requirements.txt
```
2. Obtain Google API Credentials:
- Go to Google Cloud Console.
- Create a new project or select an existing one.
- Enable the Gmail API.
- Create OAuth 2.0 credentials and download the JSON file.
- Rename the downloaded file to SECRET.json and place it in your project directory.
- On first run, the script will generate a token.pickle file for offline access.
   Follow the instructions in the Medium article (in app.py comment) to set up your API credentials and obtain SECRET.json

## Development Environment
- Operating System: Ubuntu 20.04
- Python Version: Python 3.8.10

## Usage
Run the script to fetch emails from your Gmail inbox within the last hour (you can modify this) and save them to emails.csv.
   python /path/to/fetch_emails.py

## Notes
- Ensure fetch_emails.py, SECRET.json, and token.pickle are in the same directory.
- The script fetches emails from the 'INBOX' label by default. Modify label_ids in fetch_emails() to include other labels if needed ('SENT', 'SPAM', etc.).
- Adjust timezone by modifying local_timezone in the script according to your local timezone (default is GMT +7).


