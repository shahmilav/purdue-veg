import json
import urllib.request
import urllib.parse
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer


# the Purdue dining court API url that we read from.
BASE_URL = "https://api.hfs.purdue.edu/menus/v2/locations"


def build_url(court, day=None):
    """Constructs the API url using the dining court and the current date."""

    day = day or date.today()
    return f"{BASE_URL}/{urllib.parse.quote(court)}/{day.strftime('%m-%d-%Y')}"

def fetch(url):
    """Set HTTP headers and fetch the API using urllib, returning the JSON response."""

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def has_eggs(item):
    """Returns true if eggs are in an item's allergens."""

    for a in item.get("Allergens", []):
        if a.get("Name", "").lower() in ("egg", "eggs") and a.get("Value"):
            return True
    return False

def keep(item):
    """Returns true if an item is marked as vegetarian and does not have eggs."""

    return bool(item.get("IsVegetarian")) and not has_eggs(item)

def filter_menu(data):
    """
    Filter the menu from the API.

    We use the keep() filter method to iterate through all items in the JSON response,
    and remove all items that fail the filter. The method returns a new, filtered list of 
    items for the server to serve.
    """
 
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
            # HTTP 404 as this is an invalid url path.
            self.send_response(404)
            self.end_headers()
            return

        court = urllib.parse.unquote(parts[1])

        # get the filtered body to serve.
        body = json.dumps(filter_menu(fetch(build_url(court)))).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")

        # set this header for CORS purposes as the origins do not match.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

# run the http server on port 1234
HTTPServer(("", 1234), Handler).serve_forever()
