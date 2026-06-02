import os
import re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
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


def fetch_sheet_rows(spreadsheet_id, sheet_name):
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!A:G",
        ).execute()
        rows = result.get("values", [])
        output = []
        for i, row in enumerate(rows):
            date = row[0].strip() if len(row) > 0 else ""
            topic = row[1].strip() if len(row) > 1 else ""
            col_f = row[5].strip() if len(row) > 5 else ""
            col_g = row[6].strip() if len(row) > 6 else ""
            if not date or not topic:
                continue
            if col_f or col_g:
                continue
            prompt = row[4].strip() if len(row) > 4 else ""
            line1, line2 = _parse_topic(topic)
            output.append({"date": date, "line1": line1, "line2": line2, "prompt": prompt})
        return {"ok": True, "rows": output}
    except HttpError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _parse_topic(topic):
    cleaned = re.sub(r"\s*\([^)]*\)\s*", " ", topic).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    parts = cleaned.split(" ", 1)
    line1 = parts[0] if parts else ""
    line2 = parts[1] if len(parts) > 1 else ""
    return line1, line2


def mark_row_uploaded(spreadsheet_id, sheet_name, date):
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!A:A",
        ).execute()
        rows = result.get("values", [])
        row_index = None
        for i, row in enumerate(rows):
            if row and row[0].strip() == date:
                row_index = i + 1
                break
        if row_index is None:
            return {"ok": False, "error": f"Row with date {date} not found in sheet."}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!F{row_index}",
            valueInputOption="USER_ENTERED",
            body={"values": [["TRUE"]]},
        ).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def upload_file(local_path, folder_id):
    try:
        from googleapiclient.http import MediaFileUpload
        service = get_drive_service()
        filename = os.path.basename(local_path)

        existing = service.files().list(
            q=f"name='{filename}' and '{folder_id}' in parents and trashed=false",
            fields="files(id)",
        ).execute().get("files", [])

        media = MediaFileUpload(local_path, mimetype="image/jpeg", resumable=False)

        if existing:
            service.files().update(
                fileId=existing[0]["id"],
                media_body=media,
            ).execute()
        else:
            service.files().create(
                body={"name": filename, "parents": [folder_id]},
                media_body=media,
                fields="id",
            ).execute()

        return {"ok": True, "filename": filename}
    except Exception as e:
        return {"ok": False, "filename": os.path.basename(local_path), "error": str(e)}


def list_sheet_names(spreadsheet_id):
    try:
        service = get_sheets_service()
        result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        names = [s["properties"]["title"] for s in result.get("sheets", [])]
        return {"ok": True, "sheets": names}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def test_sheets_connection(spreadsheet_id):
    try:
        service = get_sheets_service()
        result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return {"ok": True, "title": result.get("properties", {}).get("title", "")}
    except Exception as e:
        return {"ok": False, "error": str(e)}
