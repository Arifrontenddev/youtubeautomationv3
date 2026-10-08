#!/usr/bin/env python3
"""authenticate_youtube.py - One-time YouTube OAuth 2.0 Authorization

Opens browser to authenticate your Google Account and generates youtube_token.json
for automated YouTube video uploads.
"""
import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent
CLIENT_SECRETS_FILE = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "youtube_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]

def main():
    if not CLIENT_SECRETS_FILE.exists():
        print(f"Error: {CLIENT_SECRETS_FILE} not found.")
        return

    print("Initiating YouTube OAuth flow...")
    print("A browser window will open. Sign in with your Google / YouTube account and click Allow.")
    
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
    creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    print(f"\n✅ Authorization successful! Token saved to: {TOKEN_FILE}")
    print("Your YouTube Agent Studio can now publish and upload videos automatically!")

if __name__ == "__main__":
    main()
