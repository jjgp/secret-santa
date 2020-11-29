import base64
import json
import os.path
import pickle
import random
import yaml
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

email_assignments = {}
with open('emails.yaml') as f:
    emails_yml = yaml.load(f, Loader=yaml.FullLoader)
    indices = [idx for idx in range(len(emails_yml.keys()))]
    emails_to_idx = {email: idx for idx,
                     email in enumerate(emails_yml.keys())}
    idx_to_email = {idx: email for email, idx in emails_to_idx.items()}
    items = list(emails_yml.items())
    random.shuffle(items)
    for email, constraints in items:
        constraints_indices = [emails_to_idx[c]
                               for c in constraints] if constraints else []
        selection = list(
            set(indices) - set([emails_to_idx[email]] + constraints_indices)
        )
        choice = random.choice(selection)
        indices.remove(choice)
        email_assignments[email] = idx_to_email[choice]

for email, chosen in email_assignments.items():
    print(f"{email} is assigned {idx_to_email[choice]}")


# NOTE: this was copy pasta'd from:
# https://developers.google.com/gmail/api/guides/sending
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('gmail', 'v1', credentials=creds)

message = MIMEText(json.dumps(email_assignments))
message['to'] = "<paste email here>"
message['from'] = "<paste email here>"
message['subject'] = "Secret Santa Assignments"
raw_message = {
    'raw': base64.urlsafe_b64encode(
        message.as_string().encode()
    ).decode('utf-8')
}

# Call the Gmail API
message = (service.users().messages().send(userId="me", body=raw_message)
           .execute())
print('Message Id: %s' % message['id'])
