import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_token(creds)
        return creds
    return None


def run_auth_flow():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    _save_token(creds)
    return creds


def _save_token(creds):
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())


def get_sheets_service():
    creds = get_credentials()
    if not creds:
        raise RuntimeError("Not authenticated. Visit /auth first.")
    return build("sheets", "v4", credentials=creds)


def get_drive_service():
    creds = get_credentials()
    if not creds:
        raise RuntimeError("Not authenticated. Visit /auth first.")
    return build("drive", "v3", credentials=creds)


def test_sheets_connection(spreadsheet_id):
    try:
        service = get_sheets_service()
        result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return {"ok": True, "title": result.get("properties", {}).get("title", "")}
    except HttpError as e:
        return {"ok": False, "error": str(e)}
    except RuntimeError as e:
        return {"ok": False, "error": str(e)}
