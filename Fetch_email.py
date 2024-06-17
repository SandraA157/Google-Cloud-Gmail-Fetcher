from datetime import datetime, timedelta, timezone
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dateutil import parser, tz
import os
import csv
import pytz
import pickle
import re

def fetch_emails_job():
    service = initialize_gmail_service()

    emails_data = fetch_emails(service)

    save_email_data(emails_data)

def fetch_emails(service):

    local_timezone = timezone(timedelta(hours=7)) # Change hours=0 according to your timezone,  hours=7 for GMT +7 etc. 

    local_end_time = datetime.now().astimezone(local_timezone)
    local_start_time = local_end_time - timedelta(hours=1)

    utc_start_time = local_start_time.astimezone(timezone.utc)
    utc_end_time = local_end_time.astimezone(timezone.utc)

    start_epoch = int(utc_start_time.timestamp())
    end_epoch = int(utc_end_time.timestamp())

    time_range = (
        f"after:{start_epoch} "
        f"before:{end_epoch}"
    )
    
    query = time_range
    label_ids = ['INBOX'] # Other label example: 'SENT', 'SPAM', etc.
    all_emails_data = []

    for label_id in label_ids:
        nextPageToken = None
        total_emails = 0
        while True:
            result = service.users().messages().list(
                userId='me', 
                labelIds=label_id,
                maxResults=100, 
                pageToken=nextPageToken, 
                q=query
            ).execute()
            messages = result.get('messages', [])
            nextPageToken = result.get('nextPageToken')
            batch = service.new_batch_http_request()
            for msg in messages:
                batch.add(
                    service.users().messages().get(
                        userId='me', 
                        id=msg['id'], 
                        format='metadata',
                        fields='id, payload/headers'
                    ),
                    callback=lambda request_id, response, exception, all_emails_data=all_emails_data: process_email(response, all_emails_data, service)
                )
            batch.execute()

            total_emails += len(messages)
            if total_emails >= 100 or not nextPageToken:
                break

    return all_emails_data


def initialize_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('SECRET.json', SCOPES) # Change to the name of file obtained after setting your API. (Instruction on setting API: https://medium.com/@preetipriyanka24/how-to-read-emails-from-gmail-using-gmail-api-in-python-20f7d9d09ae9).
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def process_email(response, all_emails_data, service):
    if 'id' in response:
        msg_id = response['id']
        payload = response.get('payload', {})
        headers = payload.get('headers', [])

        email_data = {'Email ID': msg_id}
        for header in headers:
            if header['name'] == 'Subject':
                email_data['Subject'] = header['value']
            elif header['name'] == 'From':
                email_data['From'] = header['value']
            elif header['name'] == 'To':
                email_data['To'] = header['value']
            elif header['name'] == 'Date':
                date = header['value']
                date_object = parser.parse(date)
                
                # Convert to local timezone
                tz_offset = tz.tzoffset(None, 7 * 3600)  # +0700 is 7 hours ahead of UTC,  Adjust accoring to your timezone
                date_object = date_object.astimezone(tz_offset)
                email_data['Date'] = date_object.strftime('%a, %d %b %Y %H:%M:%S %z')
            elif header['name'] == 'Received':
                email_data['Received'] = header['value']

        parts = payload.get('parts', [])
        if parts:
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    if 'body' in part:
                        data = part['body']['data']
                        decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
                        email_data['Body'] = decoded_data.strip()
                    elif 'parts' in part:
                        for subpart in part['parts']:
                            if subpart.get('mimeType') == 'text/plain':
                                data = subpart['body']['data']
                                decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
                                email_data['Body'] = decoded_data.strip()


        label_ids = response.get('labelIds', [])
        labels = []

        for label_id in label_ids:
            label = service.users().labels().get(userId='me', id=label_id).execute()
            labels.append(label['name'])

        system_labels = service.users().labels().list(userId='me').execute()
        system_label_names = [label['name'] for label in system_labels.get('labels', [])]

        labels.extend(system_label_names)

        email_data['Labels'] = ', '.join(labels)

        all_emails_data.append(email_data)
    else:
        app.logger.error("Error processing email: No ID found in response")

def save_email_data(emails_data):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    email_csv = os.path.join(script_dir, 'emails.csv')

    with open(email_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Email ID', 'Subject', 'From', 'To', 'Date', 'Received', 'Body', 'Labels']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for email in emails_data:
            writer.writerow(email)
            print(email)

fetch_emails_job()
