import json
from time import sleep

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google_auth_oauthlib.flow
import os

from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_calendar_service(connection, db):
    with open("credentials_web.json", "r") as f:
        client_config = json.load(f)["web"]

    creds = Credentials(
        token=connection.access_token,
        refresh_token=connection.refresh_token,
        token_uri=client_config["token_uri"],
        client_id=client_config["client_id"],
        client_secret=client_config["client_secret"],
        scopes=SCOPES,
        expiry=connection.token_expiry,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        connection.access_token = creds.token
        connection.token_expiry = creds.expiry

        db.commit()

    if creds.expired and not creds.refresh_token:
        raise RuntimeError("Google Calendar connection requires reconnect")

    service = build("calendar", "v3", credentials=creds)

    return service

def create_calendar_event(service, summary, start_time, end_time):
    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Europe/Warsaw",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Europe/Warsaw",
        },
    }

    created_event = execute_with_retry(service.events().insert(
        calendarId="primary",
        body=event
    ))

    return created_event

def delete_calendar_event(service, event_id):
    execute_with_retry(service.events().delete(
        calendarId="primary",
        eventId=event_id
    ))

def get_google_authorization_url():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "credentials_web.json",
        scopes=SCOPES,
        autogenerate_code_verifier=True
    )

    flow.redirect_uri = "http://localhost:8000/integrations/google/callback"

    authorization_url, state = flow.authorization_url(
        access_type='offline',
    )

    return authorization_url, state, flow.code_verifier

def execute_with_retry(request):
    last_error = None

    for attempt in range(3):
        try:
            return request.execute()
        except HttpError as e:
            last_error = e

            if e.resp.status in {429, 500, 502, 503, 504}:
                sleep(2 ** attempt)
                continue

            raise

    raise last_error















