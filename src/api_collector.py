import time
import requests
import config

GET_OKRUG_URL = "/rs/suggest/address"
GET_KATEGORY_URL = "/interpreter"
GET_ECOLOGY_RATE_URL = "/feed/geo"
GET_ROUTING_URL = "/distancematrix"
DELAY = 1
MAX_RESULTS = 20

# Теги OpenStreetMap для каждой категории
OSM_FILTERS = {
    "metro": '["station"="subway"]',
    "bus_stop": '["highway"="bus_stop"]',
    "hospital": '["amenity"="hospital"]',
    "clinic": '["amenity"~"clinic|doctors"]',
    "school": '["amenity"="school"]',
    "kindergarten": '["amenity"="kindergarten"]',
    "restaurant": '["amenity"="restaurant"]',
    "cafe": '["amenity"="cafe"]',
    "canteen": '["amenity"~"canteen|cafeteria"]',
    "fast_food": '["amenity"="fast_food"]',
    "museum": '["tourism"="museum"]',
    "cultural_heritage": '["historic"]',
    "theatre": '["amenity"="theatre"]',
    "government": '["office"~"government|administrative"]',
    "mfc": '["name"~"МФЦ",i]',
}


class ApiCollector:
    def __init__(self, cfg: config.Parser, radius=1000):
        self.radius = radius
        self.cfg = cfg

    def geocode(self, address):
        resp = requests.get(self.cfg.yandex_api.geocode_url, params={
            "geocode": address,
            "format": "json",
            "results": 1,
            "lang": "ru_RU",
            "apikey": self.cfg.yandex_api.geocode_api_key,
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
                resp = requests.post(f"{self.cfg.yandex_api.overpass_url}", data=query, timeout=30)
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
            house = tags.get("addr:housenumber", "")
            address = f"{street} {house}".strip()

            place = {
                "name": tags.get("name", ""),
                "category": category,
                "address": address,
                "lat": p_lat,
                "lon": p_lon,
                "phone": tags.get("phone") or tags.get("contact:phone"),
                "url": tags.get("website") or tags.get("contact:website"),
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

    def get_okrug(self, address):
        resp = requests.post(f"{self.cfg.dadata_api.base_url}{GET_OKRUG_URL}",
                             params={
                                 "query": address,
                                 "count": 1,
                             },
                             headers={"Content-Type": "application/json",
                                      "Accept": "application/json",
                                      "Authorization": f"Token {self.cfg.dadata_api.api_key}"
                                      },
                             timeout=10)

        resp.raise_for_status()
        suggestions = resp.json().get("suggestions", [])
        if not suggestions:
            raise Exception(f"DaData не нашла адрес: {address}")

        data = suggestions[0].get("data", {})
        return data

    def get_ecology_rating(self, lat, lon):
        resp = requests.get(f"{self.cfg.aqicn_api}{GET_ECOLOGY_RATE_URL}:{lat};{lon}/",
                            params={
                                "token": self.cfg.aqicn_api.api_key,
                            },
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                            },
                            timeout=10)

        resp.raise_for_status()
        data = resp.json().get("suggestions", [])
        return data.get("aqi", 0)

    def get_mocsow_center_distance(self, lat, lon):
        resp = requests.get(f"{self.cfg.yandex_api.routing_url}{GET_ROUTING_URL}",
                            params={
                                "origins": f"{lat},{lon}",
                                "destinations": "55.7558,37.6176",
                                "mode": "driving",
                                "apikey": self.cfg.yandex_api.routing_api_key,
                            },
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                            },
                            timeout=10)

        resp.raise_for_status()
        rows = resp.json().get("rows", [])
        if not rows:
            return 0

        elements = rows[0].get("elements", [])
        if not elements:
            return 0

        element = elements[0]

        if element.get("status") != "OK":
            return 0

        return element.get("distance", {}).get("value", 0)
