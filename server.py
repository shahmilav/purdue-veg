import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import date

BASE_URL = "https://api.hfs.purdue.edu/menus/v2/locations"

def build_url(court, day=None):
    day = day or date.today()
    return f"{BASE_URL}/{urllib.parse.quote(court)}/{day.strftime('%m-%d-%Y')}"

def fetch(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.headers.get("Content-Type", ""), resp.read()
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} for {url}")
        print(e.read()[:300].decode("utf-8", errors="replace"))
        raise SystemExit(1)

# walk through the API response
def walk(elem, depth=0):
    text = (elem.text or "").strip()
    print("  " * depth + f"<{elem.tag}> {elem.attrib or ''} {text}")
    for child in elem:
        walk(child, depth + 1)

url = build_url("Earhart")
print("Requesting:", url)

content_type, body = fetch(url)
print("Content-Type:", content_type)

data = json.loads(body)
print(json.dumps(data, indent=2))
