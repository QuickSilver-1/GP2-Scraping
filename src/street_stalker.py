import time
import requests

# Глобальные дефайны
DELAY = 1
MAX_RESULTS = 20

# Ключ яндексового геокодера (ВЫПИЛИТЬ ИЗ КОДА ПЕРЕД КОММИТОМ)
GEOCODER_KEY = "..."

# Теги OpenStreetMap для каждой категории
OSM_FILTERS = {
    "metro":            '["station"="subway"]',
    "bus_stop":         '["highway"="bus_stop"]',
    "hospital":         '["amenity"="hospital"]',
    "clinic":           '["amenity"~"clinic|doctors"]',
    "school":           '["amenity"="school"]',
    "kindergarten":     '["amenity"="kindergarten"]',
    "restaurant":       '["amenity"="restaurant"]',
    "cafe":             '["amenity"="cafe"]',
    "canteen":          '["amenity"~"canteen|cafeteria"]',
    "fast_food":        '["amenity"="fast_food"]',
    "museum":           '["tourism"="museum"]',
    "cultural_heritage":'["historic"]',
    "theatre":          '["amenity"="theatre"]',
    "government":       '["office"~"government|administrative"]',
    "mfc":              '["name"~"МФЦ",i]',
}


class StreetStalker:
    def __init__(self, radius=1000):
        self.radius = radius
    def geocode(self, address):
        resp = requests.get("https://geocode-maps.yandex.ru/v1/", params={
            "geocode": address,
            "format":  "json",
            "results": 1,
            "lang":    "ru_RU",
            "apikey":  GEOCODER_KEY,
        }, timeout=10)
        resp.raise_for_status()
        members = resp.json()["response"]["GeoObjectCollection"]["featureMember"]
        if not members:
            raise Exception(f"Адрес не найден: {address}")
        lon_str, lat_str = members[0]["GeoObject"]["Point"]["pos"].split()
        return float(lat_str), float(lon_str)
    def search_category(self, lat, lon, category):
        query = f"""
[out:json];
nwr{OSM_FILTERS[category]}(around:{self.radius},{lat},{lon});
out center {MAX_RESULTS};
"""
        for attempt in range(3):
            try:
                resp = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=30)
                resp.raise_for_status()
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(5)
        else:
            return []
        places = []
        for el in resp.json().get("elements", []):
            tags = el.get("tags", {})
            if el["type"] == "node":
                p_lat, p_lon = el["lat"], el["lon"]
            else:
                p_lat = el.get("center", {}).get("lat", 0)
                p_lon = el.get("center", {}).get("lon", 0)

            street = tags.get("addr:street", "")
            house  = tags.get("addr:housenumber", "")
            address = f"{street} {house}".strip()

            place = {
                "name":     tags.get("name", ""),
                "category": category,
                "address":  address,
                "lat":      p_lat,
                "lon":      p_lon,
                "phone":    tags.get("phone") or tags.get("contact:phone"),
                "url":      tags.get("website") or tags.get("contact:website"),
            }
            places.append(place)

        return places
    def find(self, address, categories=None):
        if categories is None:
            categories = list(OSM_FILTERS.keys())
        lat, lon = self.geocode(address)
        result = {}
        for cat in categories:
            places = self.search_category(lat, lon, cat)
            result[cat] = places
            time.sleep(DELAY)
        return result
