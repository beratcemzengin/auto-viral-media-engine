import json

secrets_file = r'C:\Users\XXX\.gemini\antigravity\scratch\auto-viral-media-engine\kids_shorts\client_secrets.json'

with open(secrets_file) as f:
    data = json.load(f)

# Convert "web" keys to "installed" so it acts as a Desktop app for OAuth Flow compatibility
if "web" in data:
    data["installed"] = data.pop("web")
    # Redirect URIs for desktop apps should ideally be standard or oob
    data["installed"]["redirect_uris"] = ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]

with open(secrets_file, 'w') as f:
    json.dump(data, f, indent=2)

print('[OK] Converted client_secrets.json to installed (Desktop) application format.')
