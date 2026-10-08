#!/usr/bin/env python3
"""youtube_uploader.py - Direct YouTube Data API v3 Video Uploader

Uploads rendered MP4 videos directly to YouTube using Google API Client & OAuth 2.0.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

BASE_DIR = Path(__file__).resolve().parent
CLIENT_SECRETS_FILE = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "youtube_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
_current_flow = None

def get_auth_url() -> str:
    """Generate and return the Google OAuth authorization URL."""
    global _current_flow
    if not CLIENT_SECRETS_FILE.exists():
        raise FileNotFoundError(f"client_secret.json not found in {BASE_DIR}")
    
    _current_flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRETS_FILE),
        SCOPES,
        redirect_uri="http://localhost",
        autogenerate_code_verifier=False
    )
    auth_url, _ = _current_flow.authorization_url(prompt="consent", access_type="offline")
    return auth_url

def exchange_auth_code(code_or_url: str) -> Dict[str, Any]:
    """Exchange authorization code or full redirect URL for tokens and save youtube_token.json."""
    global _current_flow
    code = code_or_url.strip()
    if "code=" in code:
        import urllib.parse
        parsed = urllib.parse.urlparse(code)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            code = params["code"][0]

    flow = _current_flow if _current_flow is not None else InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRETS_FILE),
        SCOPES,
        redirect_uri="http://localhost",
        autogenerate_code_verifier=False
    )
    flow.fetch_token(code=code)
    creds = flow.credentials

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    yt = build("youtube", "v3", credentials=creds)
    resp = yt.channels().list(part="snippet", mine=True).execute()
    title = resp["items"][0]["snippet"]["title"] if resp.get("items") else "Unknown Channel"

    return {
        "status": "authenticated",
        "channel_title": title,
        "token_file": str(TOKEN_FILE)
    }

def get_youtube_service():
    """Authenticate and return an authorized YouTube service client."""
    creds = None
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRETS_FILE.exists():
                return None
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
            creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def check_youtube_connection() -> Dict[str, Any]:
    """Check if YouTube API client secret and authorization are configured."""
    has_client_secret = CLIENT_SECRETS_FILE.exists()
    has_token = TOKEN_FILE.exists()
    
    status = "disconnected"
    channel_title = None
    
    if has_client_secret and has_token:
        try:
            yt = get_youtube_service()
            if yt:
                resp = yt.channels().list(part="snippet", mine=True).execute()
                if resp.get("items"):
                    channel_title = resp["items"][0]["snippet"]["title"]
                    status = "connected"
        except Exception as e:
            status = f"auth_required: {str(e)}"
    elif has_client_secret:
        status = "ready_for_auth"

    return {
        "status": status,
        "has_client_secret": has_client_secret,
        "has_token": has_token,
        "channel_title": channel_title,
        "client_secret_path": str(CLIENT_SECRETS_FILE)
    }

def upload_video_to_youtube(
    video_file_path: str,
    title: str,
    description: str,
    tags: Optional[List[str]] = None,
    privacy_status: str = "private",
    category_id: str = "28"
) -> Dict[str, Any]:
    """Upload MP4 video file to YouTube via YouTube Data API v3."""
    if not os.path.exists(video_file_path):
        raise FileNotFoundError(f"Video file not found at: {video_file_path}")

    # Check if configured
    conn = check_youtube_connection()
    if conn["status"] != "connected":
        # Provide helpful simulated response if credentials aren't uploaded yet
        return {
            "status": "ready_for_credentials",
            "message": "YouTube API credentials required. Please place your client_secret.json in the project root to enable live direct publishing.",
            "simulated_video_id": f"sim_{os.path.basename(video_file_path).split('.')[0]}",
            "video_title": title,
            "privacy_status": privacy_status,
            "instructions": [
                "1. Go to Google Cloud Console (https://console.cloud.google.com/)",
                "2. Enable 'YouTube Data API v3'",
                "3. Create OAuth 2.0 Client ID (Desktop Application)",
                "4. Download and save as 'client_secret.json' in this folder"
            ]
        }

    yt = get_youtube_service()
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags or [],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()

    video_id = response.get("id")
    return {
        "status": "uploaded",
        "video_id": video_id,
        "watch_url": f"https://youtu.be/{video_id}",
        "studio_edit_url": f"https://studio.youtube.com/video/{video_id}/edit",
        "privacy_status": privacy_status,
        "title": title
    }
