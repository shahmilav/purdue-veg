import json
import urllib.request
import urllib.parse
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer

BASE_URL = "https://api.hfs.purdue.edu/menus/v2/locations"

def build_url(court, day=None):
    day = day or date.today()
    return f"{BASE_URL}/{urllib.parse.quote(court)}/{day.strftime('%m-%d-%Y')}"

def fetch(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def has_eggs(item):
    for a in item.get("Allergens", []):
        if a.get("Name", "").lower() in ("egg", "eggs") and a.get("Value"):
            return True
    return False

def keep(item):
    return bool(item.get("IsVegetarian")) and not has_eggs(item)

def filter_menu(data):
    meals = []
    for meal in data.get("Meals", []):
        stations = []
        for station in meal.get("Stations", []):
            items = [i["Name"] for i in station.get("Items", []) if keep(i)]
            if items:
                stations.append({"station": station["Name"], "items": items})
        if stations:
            meals.append({"meal": meal["Name"], "stations": stations})
    return {"location": data.get("Location"), "date": data.get("Date"), "meals": meals}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parts = self.path.strip("/").split("/")
        if len(parts) != 2 or parts[0] != "menu":
            self.send_response(404)
            self.end_headers()
            return
        court = urllib.parse.unquote(parts[1])
        body = json.dumps(filter_menu(fetch(build_url(court)))).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # page is on another origin
        self.end_headers()
        self.wfile.write(body)

HTTPServer(("", 1234), Handler).serve_forever()
