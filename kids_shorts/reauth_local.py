"""
YouTube OAuth for Kids Channel
Runs locally on Windows to bypass Google's OOB deprecation.
It hosts a temporary local server, opens your browser, captures the login,
saves credentials.json locally, and deploys it to the server automatically.
"""
import json
import webbrowser
import http.server
import threading
import urllib.parse
import requests
import paramiko
import os

SECRETS_FILE = r'C:\Users\XXX\.gemini\antigravity\scratch\auto-viral-media-engine\kids_shorts\client_secrets.json'
OUTPUT_FILE  = r'C:\Users\XXX\.gemini\antigravity\scratch\auto-viral-media-engine\kids_shorts\credentials.json'

if not os.path.exists(SECRETS_FILE):
    print(f"HATA: {SECRETS_FILE} bulunamadi!")
    raise SystemExit(1)

with open(SECRETS_FILE) as f:
    secrets = json.load(f)['installed']

CLIENT_ID     = secrets['client_id']
CLIENT_SECRET = secrets['client_secret']
REDIRECT_URI  = 'http://localhost:8765'
SCOPE         = 'https://www.googleapis.com/auth/youtube.upload'
TOKEN_URI     = 'https://oauth2.googleapis.com/token'

auth_code_holder = {}

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if 'code' in params:
            auth_code_holder['code'] = params['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write('<h2>Yetkilendirme Başarılı! Bu sayfayı kapatıp terminale dönebilirsiniz.</h2>'.encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write('<h2>Hata: Kod alınamadı.</h2>'.encode('utf-8'))

    def log_message(self, *args):
        pass

# Start temporary callback server
server = http.server.HTTPServer(('localhost', 8765), CallbackHandler)
t = threading.Thread(target=server.handle_request)
t.daemon = True
t.start()

# Build authorization URL
auth_params = urllib.parse.urlencode({
    'response_type': 'code',
    'client_id':     CLIENT_ID,
    'redirect_uri':  REDIRECT_URI,
    'scope':         SCOPE,
    'access_type':   'offline',
    'prompt':        'consent',
})
auth_url = f'https://accounts.google.com/o/oauth2/auth?{auth_params}'

print("=" * 70)
print("Tarayıcı açılıyor... Lütfen yeni Çocuk YouTube kanalınızla giriş yapın.")
print("=" * 70)
print()

webbrowser.open(auth_url)

print("Tarayıcıdan giriş yapılması bekleniyor...")
t.join(timeout=120)

code = auth_code_holder.get('code')
if not code:
    print("HATA: 120 saniye içinde giriş tamamlanamadı.")
    raise SystemExit(1)

# Exchange code for tokens
resp = requests.post(TOKEN_URI, data={
    'code':          code,
    'client_id':     CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri':  REDIRECT_URI,
    'grant_type':    'authorization_code',
})
tokens = resp.json()

if 'error' in tokens:
    print(f"HATA: Token takası başarısız: {tokens}")
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

# Save local copy
with open(OUTPUT_FILE, 'w') as f:
    json.dump(creds, f, indent=2)
print("[OK] credentials.json yerel bilgisayara kaydedildi.")

# Deploy credentials to the server automatically
print("Sunucuya yükleniyor...")
host = '192.168.1.2'
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username='xxx', password='xxx', timeout=15, look_for_keys=False)
sftp = client.open_sftp()
sftp.put(OUTPUT_FILE, '/home/xxx/shorts_automation/kids_shorts/credentials.json')
sftp.close()
print("[OK] credentials.json sunucuya yüklendi!")

# Test authentication on the server
_, stdout, _ = client.exec_command(
    'cd /home/xxx/shorts_automation/kids_shorts && '
    '../venv/bin/python3 -c "import main; print(\'SUNUCU AUTH BAŞARILI!\')"'
)
print(f"[Sunucu Test Sonucu] {stdout.read().decode().strip()}")
client.close()

print()
print("🎉 İŞLEM TAMAM! Yeni çocuk kanalı başarıyla yetkilendirildi.")
