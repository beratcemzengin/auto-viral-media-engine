"""
YouTube OAuth - OOB (Out-of-Band) Flow
This script is executed locally (on a machine with a web browser).
It prints a Google authorization link, redirects to a browser,
accepts the response code, and writes a permanent credentials.json file.
"""
import os
import json
import urllib.parse
import requests

SECRETS_FILE = os.path.join('shorts_automation', 'client_secrets.json')
OUTPUT_FILE  = os.path.join('shorts_automation', 'credentials.json')

if not os.path.exists(SECRETS_FILE):
    print(f"ERROR: {SECRETS_FILE} not found. Please place your client_secrets.json in shorts_automation/ first.")
    raise SystemExit(1)

with open(SECRETS_FILE) as f:
    secrets = json.load(f)['installed']

CLIENT_ID     = secrets['client_id']
CLIENT_SECRET = secrets['client_secret']
REDIRECT_URI  = 'urn:ietf:wg:oauth:2.0:oob'
SCOPE         = 'https://www.googleapis.com/auth/youtube.upload'
TOKEN_URI     = 'https://oauth2.googleapis.com/token'

auth_params = urllib.parse.urlencode({
    'response_type': 'code',
    'client_id':     CLIENT_ID,
    'redirect_uri':  REDIRECT_URI,
    'scope':         SCOPE,
    'access_type':   'offline',
    'prompt':        'consent',
})
auth_url = f'https://accounts.google.com/o/oauth2/auth?{auth_params}'

print("=" * 60)
print("1. Open the following URL in your web browser:")
print("=" * 60)
print()
print(auth_url)
print()
print("2. Sign in and authorize the application.")
print("3. Google will present an Authorization Code on screen.")
code = input("4. Paste that authorization code here: ").strip()

print("\nExchanging code for permanent tokens...")
resp = requests.post(TOKEN_URI, data={
    'code':          code,
    'client_id':     CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri':  REDIRECT_URI,
    'grant_type':    'authorization_code',
})
tokens = resp.json()

if 'error' in tokens:
    print(f"\nERROR: Failed to exchange token: {tokens}")
    raise SystemExit(1)

creds = {
    'token':          tokens['access_token'],
    'refresh_token':  tokens.get('refresh_token', ''),
    'token_uri':      TOKEN_URI,
    'client_id':      CLIENT_ID,
    'client_secret':  CLIENT_SECRET,
    'scopes':         [SCOPE],
    'universe_domain':'googleapis.com',
    'account':        '',
    'expiry':         None,
}

# Ensure directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

with open(OUTPUT_FILE, 'w') as f:
    json.dump(creds, f, indent=2)

print(f"\n[SUCCESS] credentials.json saved successfully to {OUTPUT_FILE}")
print("You can now transfer this credentials.json to your production server.")
print(f"Refresh Token: {creds['refresh_token'][:30]}...")
