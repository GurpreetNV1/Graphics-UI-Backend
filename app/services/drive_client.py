# app/services/drive_client.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

from app.config import settings

SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        settings.google_service_account_path, scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials)


def create_folder(name: str, parent_id: str) -> dict:
    """Creates a folder inside parent_id, returns {id, link}."""
    service = _get_drive_service()
    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(
        body=file_metadata,
        fields="id, webViewLink",
        supportsAllDrives=True,
    ).execute()
    return {"id": folder["id"], "link": folder.get("webViewLink")}


def upload_file(file_bytes: bytes, filename: str, mime_type: str, parent_id: str) -> dict:
    """Uploads a file into parent_id, returns {id, link}."""
    service = _get_drive_service()
    file_metadata = {"name": filename, "parents": [parent_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink, webContentLink",
        supportsAllDrives=True,
    ).execute()
    return {
        "id": file["id"],
        "view_link": file.get("webViewLink"),
        "download_link": file.get("webContentLink"),
    }


def list_files_in_folder(folder_id: str) -> list[dict]:
    """Lists files inside a folder with their links."""
    service = _get_drive_service()
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, webViewLink, webContentLink, mimeType, createdTime)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    return results.get("files", [])


def delete_file(file_id: str) -> None:
    """Permanently deletes a file (used if a raw file needs removing)."""
    service = _get_drive_service()
    service.files().delete(
        fileId=file_id,
        supportsAllDrives=True,
    ).execute()


def set_domain_permission(file_id: str, domain: str, allow_download: bool):
    """Grants domain-wide view access to a file, and toggles whether download/copy is allowed."""
    service = _get_drive_service()

    service.permissions().create(
        fileId=file_id,
        body={"type": "domain", "role": "reader", "domain": domain},
        supportsAllDrives=True,
    ).execute()

    service.files().update(
        fileId=file_id,
        body={"copyRequiresWriterPermission": not allow_download},
        supportsAllDrives=True,
    ).execute()