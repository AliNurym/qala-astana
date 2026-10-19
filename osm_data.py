"""OpenStreetMap POI collector for Qala Astana.

Supports:
- Overpass API queries covering Astana Center, Expo, Mega Silk Way, and surrounding zones.
- Source-linked POI facts from OpenStreetMap, including descriptions, hours, and contact tags when present.
- Explicit feature tags only; unknown amenities stay unknown.
- Seamless caching in data/places.json with graceful offline fallback.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "places.json"
OVERPASS_URLS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
)
USER_AGENT = "QalaCityGuide/2.0 (Astana Smart City Hackathon AI Assistant)"

# Keep collection bounded to the areas used by the demo instead of querying the
# large empty corridor between the city and NQZ airport.
COVERAGE_AREAS = {
    "central_astana": (51.070, 71.330, 51.175, 71.520),
    "nqz_airport": (51.015, 71.430, 51.040, 71.490),
}
BBOX = (
    min(area[0] for area in COVERAGE_AREAS.values()),
    min(area[1] for area in COVERAGE_AREAS.values()),
    max(area[2] for area in COVERAGE_AREAS.values()),
    max(area[3] for area in COVERAGE_AREAS.values()),
)

TAGS = {
    "aeroway": {"terminal"},
    "amenity": {
        "cafe", "restaurant", "fast_food", "food_court", "bar", "pub",
        "ice_cream", "library", "arts_centre", "theatre", "cinema",
        "marketplace", "fountain",
    },
    "tourism": {
        "attraction", "museum", "viewpoint", "gallery", "artwork", "zoo",
        "theme_park", "information",
    },
    "leisure": {"park", "playground", "garden", "sports_centre", "ice_rink"},
    "historic": {"monument", "memorial", "castle", "ruins"},
    "shop": {"mall"},
}

CATEGORY_LABELS = {
    "airport_terminal": "Терминал аэропорта",
    "cafe": "Кафе",
    "restaurant": "Ресторан",
    "fast_food": "Быстрая еда",
    "food_court": "Фуд-корт",
    "bar": "Бар",
    "pub": "Паб",
    "ice_cream": "Мороженое",
    "library": "Библиотека",
    "arts_centre": "Арт-пространство",
    "theatre": "Театр",
    "cinema": "Кинотеатр",
    "marketplace": "Рынок",
    "fountain": "Фонтан",
    "attraction": "Достопримечательность",
    "museum": "Музей",
    "viewpoint": "Смотровая площадка",
    "gallery": "Галерея",
    "artwork": "Арт-объект",
    "zoo": "Зоопарк",
    "theme_park": "Парк развлечений",
    "information": "Информационный центр",
    "park": "Парк",
    "playground": "Детская площадка",
    "garden": "Сад",
    "sports_centre": "Спортивный центр",
    "ice_rink": "Каток",
    "monument": "Памятник",
    "memorial": "Мемориал",
    "castle": "Историческое место",
    "ruins": "Историческое место",
    "mall": "Торговый центр",
}

# Handwritten POI records stay disabled until their claims have traceable sources.
CURATED_REGISTRY: list[dict] = []

def build_query() -> str:
    clauses = []
    for south, west, north, east in COVERAGE_AREAS.values():
        bbox = f"{south},{west},{north},{east}"
        for key, values in TAGS.items():
            pattern = "|".join(sorted(values))
            clauses.append(f'nwr["name"]["{key}"~"^({pattern})$"]({bbox});')
        clauses.append(f'nwr["leisure"="playground"]({bbox});')
    return "[out:json][timeout:45];\n(\n" + "\n".join(clauses) + "\n);\nout center tags;"


def point_in_coverage(lat: float, lon: float) -> bool:
    return any(
        south <= lat <= north and west <= lon <= east
        for south, west, north, east in COVERAGE_AREAS.values()
    )


def category_for(tags: dict[str, str]) -> tuple[str, str]:
    if tags.get("aeroway") == "terminal":
        return "airport_terminal", CATEGORY_LABELS["airport_terminal"]
    for key in ("leisure", "tourism", "historic", "amenity", "shop"):
        value = tags.get(key)
        if value and value in CATEGORY_LABELS:
            return value, CATEGORY_LABELS[value]
    return "place", "Место"


def short_summary(category_label: str, description: str, tags: dict[str, str]) -> tuple[str, str]:
    if description:
        return description, "osm_description"
    details = []
    if tags.get("cuisine"):
        details.append("кухня: " + tags["cuisine"].replace(";", ", "))
    if tags.get("wheelchair"):
        details.append("доступность: " + tags["wheelchair"])
    if tags.get("opening_hours"):
        details.append("часы: " + tags["opening_hours"])
    return " · ".join([category_label, *details]), "osm_category_tags"


def derive_features(name: str, category: str, tags: dict[str, str]) -> dict:
    """Return only explicit amenity tags; leave uncollected attributes unknown."""
    del name, category  # Kept in the signature for compatibility with local callers.
    wifi_tag = str(tags.get("wifi", "")).casefold()
    internet_tag = str(tags.get("internet_access", "")).casefold()
    socket_tags = [
        str(value).casefold()
        for key, value in tags.items()
        if key == "socket" or key.startswith("socket:")
    ]
    socket_values = {"yes", "designated", "customers", "public"}
    explicit_socket = (
        True if any(value in socket_values for value in socket_tags)
        else False if socket_tags and all(value == "no" for value in socket_tags)
        else None
    )
    quiet_tag = str(tags.get("quiet", "")).casefold()
    explicit_quiet = True if quiet_tag == "yes" else (False if quiet_tag == "no" else None)
    return {
        "is_night": None,
        "kids_friendly": None,
        "is_group_friendly": None,
        "wheelchair": tags.get("wheelchair") or None,
        "has_sockets": explicit_socket,
        "has_wifi": True if wifi_tag in {"yes", "wlan"} or internet_tag == "wlan" else (False if wifi_tag == "no" else None),
        "is_quiet": explicit_quiet,
    }


def normalize_element(element: dict) -> dict | None:
    tags = element.get("tags") or {}
    name_ru = tags.get("name:ru") or ""
    name_kk = tags.get("name:kk") or ""
    name_en = tags.get("name:en") or ""
    raw_name = tags.get("name") or name_ru or name_kk or name_en
    if not raw_name and tags.get("leisure") == "playground":
        raw_name = "Детская площадка"
        name_ru = "Детская площадка"
        name_kk = "Балалар алаңы"
        name_en = "Children Playground"

    if not raw_name:
        return None

    name = str(name_ru or raw_name).strip()

    lat = element.get("lat")
    lon = element.get("lon")
    if lat is None or lon is None:
        center = element.get("center") or {}
        lat, lon = center.get("lat"), center.get("lon")
    if lat is None or lon is None:
        return None

    category, category_label = category_for(tags)
    element_type = element.get("type", "node")
    element_id = str(element.get("id", ""))
    full_id = f"{element_type}/{element_id}"

    description = (tags.get("description:ru") or tags.get("description") or "").strip()
    description_kk = (tags.get("description:kk") or "").strip()
    description_en = (tags.get("description:en") or "").strip()

    summary, summary_source = short_summary(category_label, description, tags)
    features = derive_features(name, category, tags)
    capacity_raw = tags.get("capacity") or tags.get("seats") or ""
    capacity_match = re.fullmatch(r"\s*(\d+)\s*", str(capacity_raw))
    capacity = int(capacity_match.group(1)) if capacity_match else None

    return {
        "id": full_id,
        "name": name,
        "name_kk": name_kk or name,
        "name_en": name_en or name,
        "name_source_language": "ru" if tags.get("name:ru") else ("kk" if tags.get("name:kk") else ("en" if tags.get("name:en") else "und")),
        "lat": float(lat),
        "lon": float(lon),
        "category": category,
        "category_label": category_label,
        "description": description[:500],
        "description_kk": description_kk[:500],
        "description_en": description_en[:500],
        "short_summary": summary[:500],
        "short_summary_source": summary_source,
        "opening_hours": tags.get("opening_hours", ""),
        "website": tags.get("website") or tags.get("contact:website", ""),
        "phone": tags.get("phone") or tags.get("contact:phone", ""),
        "cuisine": tags.get("cuisine", ""),
        "capacity": capacity,
        "capacity_source": "capacity" if tags.get("capacity") else ("seats" if tags.get("seats") else ""),
        "wheelchair": features["wheelchair"],
        "kids_friendly": features["kids_friendly"],
        "is_group_friendly": features["is_group_friendly"],
        "is_night": features["is_night"],
        "has_sockets": features["has_sockets"],
        "has_wifi": features["has_wifi"],
        "is_quiet": features["is_quiet"],
        "source": "OpenStreetMap",
        "source_url": f"https://www.openstreetmap.org/{element_type}/{element_id}",
    }


def collect_places() -> dict:
    """Collect from Overpass; keep the last successful cache when it is unavailable."""
    unique: dict[str, dict] = {}
    attempted_at = datetime.now(timezone.utc).isoformat()
    previous: dict = {}
    fetch_errors: list[str] = []
    query = build_query()
    body = urlencode({"data": query}).encode("utf-8")
    fetched = 0
    successful_response = False
    for endpoint in OVERPASS_URLS:
        request = Request(
            endpoint,
            data=body,
            headers={
                "User-Agent": USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=35) as response:
                payload = json.loads(response.read().decode("utf-8"))
            successful_response = True
            for element in payload.get("elements", []):
                place = normalize_element(element)
                if place:
                    unique[place["id"]] = place
                    fetched += 1
            if fetched > 0:
                break
        except (HTTPError, URLError, TimeoutError, ValueError):
            fetch_errors.append(endpoint)
            continue

    # A zero-result response is not enough evidence to replace a useful saved catalog.
    if fetched == 0 and DATA_PATH.exists():
        try:
            previous = json.loads(DATA_PATH.read_text(encoding="utf-8"))
            for cached_place in previous.get("places", []):
                place = dict(cached_place)
                pid = place.get("id")
                if pid and not pid.startswith("curated/") and place.get("source") == "OpenStreetMap":
                    for field in ("rating", "reviews_count", "events"):
                        place.pop(field, None)
                    unique[pid] = place
        except Exception:
            pass

    places = sorted(unique.values(), key=lambda item: (item["category_label"], item["name"].casefold()))
    collection_status = "refreshed" if fetched else ("cache_fallback" if places else "unavailable")
    updated_at = attempted_at if fetched else previous.get("updated_at", "")
    default_areas = [{"id": area_id, "bbox": list(bounds)} for area_id, bounds in COVERAGE_AREAS.items()]
    collected_areas = (
        default_areas
        if fetched
        else previous.get("coverage_areas") or default_areas
    )
    return {
        "source": "OpenStreetMap (Overpass)",
        "license": "OpenStreetMap data: ODbL 1.0",
        "bbox": list(BBOX),
        "coverage_areas": collected_areas,
        "requested_coverage_areas": [
            {"id": area_id, "bbox": list(bounds)}
            for area_id, bounds in COVERAGE_AREAS.items()
        ],
        "updated_at": updated_at,
        "last_attempt_at": attempted_at,
        "collection_status": collection_status,
        "collection_response_received": successful_response,
        "collection_error_count": len(fetch_errors),
        "fetched_count": fetched,
        "count": len(places),
        "places": places,
    }


def save_places(payload: dict) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = DATA_PATH.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(DATA_PATH)


def sync_places() -> dict:
    payload = collect_places()
    save_places(payload)
    return payload


if __name__ == "__main__":
    result = sync_places()
    print(f"Сохранено POI мест: {result['count']}")
    print(f"Файл: {DATA_PATH}")
