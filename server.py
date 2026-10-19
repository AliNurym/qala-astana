"""Qala Astana — local POI retrieval and walking recommendation prototype.

Retrieves source-linked OpenStreetMap POIs, ranks them with lexical, intent, and
distance signals, then returns a generated visit idea. Unknown amenities remain
unknown; the local cache is retained when Overpass cannot provide fresh data.
"""

from __future__ import annotations

import json
import math
import os
import re
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from osm_data import (
    CATEGORY_LABELS,
    COVERAGE_AREAS,
    DATA_PATH,
    point_in_coverage,
    short_summary,
    sync_places,
)

ROOT = Path(__file__).resolve().parent
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8765"))
DATA_TTL_SECONDS = 24 * 60 * 60
MAX_DISTANCE_KM = 12.0
SERVER_START_TIME = time.time()
RATE_LIMIT_MAX_PER_MINUTE = 120
LOCAL_GENERATOR = "local_template"

CATEGORY_LABELS_I18N = {
    "ru": CATEGORY_LABELS,
    "kk": {
        "airport_terminal": "Әуежай терминалы",
        "cafe": "Кофехана", "restaurant": "Мейрамхана", "fast_food": "Фастфуд",
        "food_court": "Фуд-корт", "bar": "Бар", "pub": "Паб", "ice_cream": "Балмұздақ",
        "library": "Кітапхана", "arts_centre": "Өнер кеңістігі", "theatre": "Театр",
        "cinema": "Кинотеатр", "marketplace": "Базар", "fountain": "Субұрқақ",
        "attraction": "Көрікті жер", "museum": "Мұражай", "viewpoint": "Көрініс алаңы",
        "gallery": "Галерея", "artwork": "Өнер нысаны", "zoo": "Хайуанаттар бағы",
        "theme_park": "Ойын-сауық саябағы", "information": "Ақпарат орталығы",
        "park": "Саябақ", "playground": "Балалар алаңы", "garden": "Бақ",
        "sports_centre": "Спорт орталығы", "ice_rink": "Мұз айдыны", "monument": "Ескерткіш",
        "memorial": "Мемориал", "castle": "Тарихи орын", "ruins": "Тарихи орын", "mall": "Сауда орталығы",
    },
    "en": {
        "airport_terminal": "Airport terminal",
        "cafe": "Cafe", "restaurant": "Restaurant", "fast_food": "Fast food",
        "food_court": "Food court", "bar": "Bar", "pub": "Pub", "ice_cream": "Ice cream",
        "library": "Library", "arts_centre": "Arts centre", "theatre": "Theatre",
        "cinema": "Cinema", "marketplace": "Market", "fountain": "Fountain",
        "attraction": "Attraction", "museum": "Museum", "viewpoint": "Viewpoint",
        "gallery": "Gallery", "artwork": "Artwork", "zoo": "Zoo", "theme_park": "Theme park",
        "information": "Information centre", "park": "Park", "playground": "Playground",
        "garden": "Garden", "sports_centre": "Sports centre", "ice_rink": "Ice rink",
        "monument": "Monument", "memorial": "Memorial", "castle": "Historic site",
        "ruins": "Historic site", "mall": "Shopping centre",
    },
}


def localized_category_label(category: str, lang: str) -> str:
    labels = CATEGORY_LABELS_I18N.get(lang, CATEGORY_LABELS_I18N["ru"])
    return labels.get(category, CATEGORY_LABELS.get(category, category or "место"))

SYNC_STATE = {"syncing": False, "error": "", "started_at": ""}
SYNC_LOCK = threading.Lock()
_DATASET_CACHE: dict[str, any] = {"mtime": 0.0, "data": None}
_RATE_LIMIT_LOCK = threading.Lock()
_CLIENT_REQUESTS: dict[str, list[float]] = {}


def check_rate_limit(client_ip: str) -> bool:
    """Sliding-window IP rate limiter to protect backend against DDoS."""
    now = time.time()
    cutoff = now - 60.0
    with _RATE_LIMIT_LOCK:
        history = _CLIENT_REQUESTS.get(client_ip, [])
        history = [t for t in history if t > cutoff]
        if len(history) >= RATE_LIMIT_MAX_PER_MINUTE:
            return False
        history.append(now)
        _CLIENT_REQUESTS[client_ip] = history
        if len(_CLIENT_REQUESTS) > 1000:
            for ip in list(_CLIENT_REQUESTS.keys()):
                _CLIENT_REQUESTS[ip] = [t for t in _CLIENT_REQUESTS[ip] if t > cutoff]
                if not _CLIENT_REQUESTS[ip]:
                    del _CLIENT_REQUESTS[ip]
        return True


def get_astana_hour() -> int:
    """Current Astana local hour (UTC+5) for dynamic diurnal relevance."""
    utc_now = datetime.now(timezone.utc)
    return (utc_now.hour + 5) % 24


def make_navigation_links(origin: tuple[float, float], destination: tuple[float, float]) -> dict[str, str]:
    """Generate instant 1-click deep links for 2GIS, Google Maps, and Yandex Maps."""
    orig_lat, orig_lon = origin
    dest_lat, dest_lon = destination
    return {
        "twogis_url": f"https://2gis.kz/astana/geo/{dest_lon}%2C{dest_lat}",
        "google_maps_url": f"https://www.google.com/maps/dir/?api=1&origin={orig_lat},{orig_lon}&destination={dest_lat},{dest_lon}&travelmode=walking",
        "yandex_maps_url": f"https://yandex.kz/maps/163/astana/?rtext={orig_lat}%2C{orig_lon}~{dest_lat}%2C{dest_lon}&rtt=pd",
    }


# Multilingual Stop Words
STOP_WORDS = {
    "ru": {
        "я", "мне", "мы", "сейчас", "хочу", "ищу", "рядом", "возле", "недалеко",
        "что", "куда", "где", "есть", "для", "на", "в", "и", "или", "пешком",
        "можно", "посмотреть", "место", "места", "пойти", "сходить", "час",
        "минут", "минуту", "минуты", "сегодня", "астана", "astana", "подскажи",
        "посоветуй", "посоветуете", "быстро", "хорошее", "просто",
    },
    "kk": {
        "мен", "біз", "қазір", "жанында", "қасында", "қайда", "не", "бар",
        "үшін", "және", "немесе", "жаяу", "болады", "көруге", "орын", "бару",
        "сағат", "минут", "бүгін", "астана", "көрсет", "кеңес", "бер",
    },
    "en": {
        "i", "me", "we", "now", "want", "looking", "near", "nearby", "around",
        "what", "where", "is", "for", "in", "at", "and", "or", "walk", "walking",
        "can", "see", "place", "places", "go", "hour", "hours", "minute", "minutes",
        "today", "astana", "suggest", "recommend",
    },
}

INTENT_TERMS = {
    "cafe": {"кафе", "кофе", "coffee", "кофейня", "розет", "тих", "чай", "кофехана", "bakery", "десерт", "завтрак", "breakfast", "ноутбук", "поработать", "круассан"},
    "park": {"парк", "прогул", "природ", "зелень", "сад", "саябақ", "бульвар", "аллея", "паркі", "набережн", "сквер", "жағалау"},
    "playground": {"дет", "ребен", "ребён", "площадк", "игров", "бала", "балалар", "kid", "kids", "playground", "семейн", "качел"},
    "museum": {"музей", "выстав", "истори", "культур", "мұражай", "экспозиц", "көрме", "интерактив", "галере", "арт", "картин"},
    "attraction": {"необыч", "интерес", "вид", "увид", "смотров", "достопримеч", "көрікті", "панорам", "сфера", "байтерек", "экспо", "expo", "sight", "view", "фото", "селфи"},
    "restaurant": {"еда", "обед", "ужин", "ресторан", "поесть", "мейрамхана", "тамақ", "food", "dinner", "lunch", "стейк", "плов", "кухн"},
    "night": {"ноч", "вечер", "поздн", "түн", "кеш", "night", "bar", "бар", "паб", "pub", "подсветк", "лаунж", "lounge", "коктейл"},
    "group": {"групп", "компан", "друзь", "топ", "достар", "group", "friends", "3-5", "вместе", "коллег"},
    "accessibility": {"коляск", "инвалид", "пандус", "доступн", "арба", "кедергісіз", "wheelchair", "accessible", "безбарьер"},
}

CATEGORY_GROUPS = {
    "cafe": {"cafe", "ice_cream"},
    "park": {"park", "garden"},
    "playground": {"playground", "theme_park"},
    "museum": {"museum", "gallery", "arts_centre"},
    "attraction": {"attraction", "viewpoint", "monument", "memorial", "artwork"},
    "restaurant": {"restaurant", "fast_food", "food_court", "bar", "pub"},
}

VISIT_TIME_ESTIMATES = {
    "cafe": (25, 45),
    "ice_cream": (10, 20),
    "restaurant": (35, 60),
    "fast_food": (15, 30),
    "food_court": (20, 40),
    "bar": (40, 90),
    "pub": (45, 90),
    "park": (30, 60),
    "garden": (20, 40),
    "playground": (25, 50),
    "museum": (45, 90),
    "gallery": (30, 60),
    "arts_centre": (30, 60),
    "viewpoint": (15, 30),
    "monument": (10, 20),
    "memorial": (10, 20),
    "artwork": (5, 15),
    "attraction": (20, 40),
    "zoo": (60, 120),
    "theme_park": (45, 90),
    "cinema": (90, 150),
    "theatre": (90, 150),
    "mall": (30, 75),
    "sports_centre": (45, 90),
    "ice_rink": (45, 90),
}


def load_dotenv() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value


def read_dataset() -> dict:
    if not DATA_PATH.exists():
        return {"source": "OpenStreetMap", "updated_at": "", "count": 0, "places": []}
    try:
        mtime = DATA_PATH.stat().st_mtime
        if _DATASET_CACHE["data"] is not None and _DATASET_CACHE["mtime"] == mtime:
            return _DATASET_CACHE["data"]
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        _DATASET_CACHE["mtime"] = mtime
        _DATASET_CACHE["data"] = data
        return data
    except (OSError, json.JSONDecodeError):
        return {"source": "OpenStreetMap", "updated_at": "", "count": 0, "places": []}


def parse_timestamp(value: str) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def start_sync(force: bool = False) -> bool:
    with SYNC_LOCK:
        if SYNC_STATE["syncing"]:
            return False
        data = read_dataset()
        age = time.time() - parse_timestamp(data.get("updated_at", ""))
        present_areas = {area.get("id") for area in data.get("coverage_areas", []) if isinstance(area, dict)}
        expected_areas = set(COVERAGE_AREAS)
        coverage_refresh_needed = not expected_areas.issubset(present_areas)
        if not force and data.get("places") and age < DATA_TTL_SECONDS and not coverage_refresh_needed:
            return False
        SYNC_STATE.update({"syncing": True, "error": "", "started_at": datetime.now(timezone.utc).isoformat()})

    def worker() -> None:
        try:
            result = sync_places()
            if result.get("collection_status") == "refreshed":
                SYNC_STATE["error"] = ""
                print(f"OpenStreetMap обновлён: {result['count']} POI")
            else:
                SYNC_STATE["error"] = "Overpass не вернул свежие POI; сохранённый каталог оставлен без изменения даты обновления."
                print(SYNC_STATE["error"])
        except Exception as error:
            SYNC_STATE["error"] = str(error)[:300]
            print(f"Сбор POI не завершился: {error}")
        finally:
            SYNC_STATE["syncing"] = False

    threading.Thread(target=worker, name="osm-sync", daemon=True).start()
    return True


def llm_provider() -> str:
    load_dotenv()
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return "openai"
    if os.environ.get("GEMINI_API_KEY", "").strip():
        return "gemini"
    if os.environ.get("DEEPSEEK_API_KEY", "").strip():
        return "deepseek"
    return LOCAL_GENERATOR


def get_status() -> dict:
    data = read_dataset()
    source_counts: dict[str, int] = {}
    for place in data.get("places", []):
        source = str(place.get("source") or "Источник не указан")
        source_counts[source] = source_counts.get(source, 0) + 1
    provider = llm_provider()
    external_llm_note = (
        " Внешний ИИ настроен, но получает запрос и выбранные POI только после согласия в форме."
        if provider != LOCAL_GENERATOR
        else " Внешний ИИ не настроен; используется локальный режим."
    )
    hour = get_astana_hour()
    astana_now = datetime.now(timezone.utc)
    astana_minute = astana_now.minute
    astana_time_str = f"{(astana_now.hour + 5) % 24:02d}:{astana_minute:02d}"
    
    if 5 <= hour < 12:
        period = "Утро в Астане"
        period_icon = "wb_sunny"
    elif 12 <= hour < 17:
        period = "День в Астане"
        period_icon = "light_mode"
    elif 17 <= hour < 22:
        period = "Вечер в Астане"
        period_icon = "wb_twilight"
    else:
        period = "Ночь в Астане"
        period_icon = "bedtime"

    return {
        "poi_count": len(data.get("places", [])),
        "updated_at": data.get("updated_at", ""),
        "last_attempt_at": data.get("last_attempt_at", ""),
        "collection_status": data.get("collection_status", "legacy_cache"),
        "collection_response_received": data.get("collection_response_received", False),
        "source_counts": source_counts,
        "syncing": SYNC_STATE["syncing"],
        "sync_error": SYNC_STATE["error"],
        "llm_enabled": provider != LOCAL_GENERATOR,
        "llm_requires_opt_in": True,
        "llm_provider": provider,
        "generation_engine": "local_retrieval_templates_default",
        "astana_time": astana_time_str,
        "astana_hour": hour,
        "astana_period": period,
        "astana_period_icon": period_icon,
        "routing_enabled": bool(os.environ.get("ORS_API_KEY")),
        "routing_privacy_note": {
            "ru": (
                "Точка не сохраняется. OpenStreetMap получает тайлы видимой области карты; ORS — координаты при расчёте."
                + external_llm_note
            ),
            "kk": (
                "Нүкте сақталмайды. OpenStreetMap карта көрінісінің тайлдарын алады; маршрут есебінде ORS координаттарды алады."
                + (" Сыртқы ЖИ деректерді тек нысандағы келісімнен кейін алады." if provider != LOCAL_GENERATOR else " Сыртқы ЖИ бапталмаған; жергілікті режим қолданылады.")
            ),
            "en": (
                "The point is not stored. OpenStreetMap receives tiles for the visible map area; ORS receives coordinates when routing."
                + (" The external AI receives data only after form consent." if provider != LOCAL_GENERATOR else " No external AI is configured; local generation is used.")
            ),
        },
        "source": data.get("source", "OpenStreetMap (Overpass)"),
        "license": data.get("license", "OpenStreetMap data: ODbL 1.0"),
        "coverage_areas": data.get("coverage_areas", [
            {"id": "central_astana", "bbox": list(COVERAGE_AREAS["central_astana"])}
        ]),
        "stretch_goals_supported": [
            "mini_route",
            "multilingual",
            "official_events_calendar_link",
        ],
        "stretch_goals_partial": {
            "group_planning": "group size can be selected; explicit venue capacity is used only when present, otherwise fit is unknown",
            "accessibility": "only explicit wheelchair=yes destinations are eligible; a wheelchair route is verified only when ORS returns one",
            "local_events": "official Visit Astana calendar link is provided; event records are not imported from an undocumented feed",
        },
        "events_source_url": "https://www.visitastana.kz/en/about-city/where-to-go/",
        "map_tile_providers": ["OpenStreetMap"],
    }


def get_health() -> dict:
    """Detailed health check and POI category distribution telemetry."""
    data = read_dataset()
    places = data.get("places", [])
    categories: dict[str, int] = {}
    for item in places:
        cat = item.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "status": "healthy",
        "service": "Qala Astana 2.0 Recommendations Engine",
        "version": "2.0.0",
        "uptime_seconds": round(time.time() - SERVER_START_TIME, 1),
        "astana_time": datetime.now(timezone.utc).isoformat(),
        "astana_hour": get_astana_hour(),
        "poi_total": len(places),
        "categories_count": len(categories),
        "poi_by_category": categories,
        "cache_active": _DATASET_CACHE["data"] is not None,
        "llm_provider": llm_provider(),
        "routing_engine": "OpenRouteService (profile depends on request)" if os.environ.get("ORS_API_KEY") else "Approximate distance estimate (Haversine × 1.35)",
    }


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    value = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * radius * math.asin(min(1.0, math.sqrt(value)))


def normalize_text(value: str) -> str:
    return " ".join(re.findall(r"[a-zа-яёәғқңөұүһі0-9]+", value.casefold()))


def category_matches(selected_category: str, actual_category: str) -> bool:
    if selected_category in {"", "all"}:
        return True
    return actual_category in CATEGORY_GROUPS.get(selected_category, {selected_category})


def query_intents(query: str) -> set[str]:
    tokens = normalize_text(query).split()
    matched = set()
    for intent, terms in INTENT_TERMS.items():
        if any(token.startswith(term) for token in tokens for term in terms):
            matched.add(intent)
    return matched


def parse_time_budget(query: str) -> dict | None:
    text = query.casefold()
    values: list[int] = []
    pattern = re.compile(
        r"(?P<start>\d{1,3})(?:\s*[-–—]\s*(?P<end>\d{1,3}))?\s*"
        r"(?P<unit>минут\w*|мин\.?|час\w*|ч\.?|сағат\w*|hour\w*|min\w*)(?![а-яёәғқңөұүһіa-z])",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        unit = match.group("unit").lower()
        multiplier = 60 if any(h in unit for h in ("час", "ч", "сағ", "hour")) else 1
        end = int(match.group("end") or match.group("start"))
        values.append(max(1, min(480, end * multiplier)))

    if re.search(r"полтора\s+час|жарым\s+сағат|1\.5\s*h", text):
        values.append(90)
    elif re.search(r"полчас(?:а)?|жарты\s+сағат|half\s*an?\s*hour", text):
        values.append(30)
    else:
        if re.search(r"\b(?:пара|пару)\s+(?:час\w*|ч\.?)|\ba\s+couple\s+of\s+hours\b", text):
            values.append(120)
        word_hours = {
            "один": 60, "одна": 60, "два": 120, "две": 120, "три": 180,
            "бір": 60, "екі": 120, "үш": 180,
            "one": 60, "two": 120, "three": 180,
        }
        for word, minutes in word_hours.items():
            if re.search(rf"\b{word}\s+(?:час|сағат|hour)", text):
                values.append(minutes)

    if not values:
        return None

    walking_context = bool(re.search(
        r"в\s+пути|на\s+дорогу|пешком\s+(?:до|в\s+пути)|время\s+пешком|прогуляться|прогулк\w*|пройтись|серуен\w*|жаяу\s+жол|walking\s+time|walk\s+duration|\bwalk\b|\bstroll\b",
        text,
    ))
    return {
        "minutes": max(values),
        "mode": "walk" if walking_context else "total",
    }


def parse_group_size(text: str, requested: object = None) -> int:
    try:
        value = int(requested)
        if 3 <= value <= 5:
            return value
    except (TypeError, ValueError):
        pass
    match = re.search(r"\b([3-5])\s*(?:чел(?:овек)?|людей|адам|people|persons|pax)\b", text.casefold())
    return int(match.group(1)) if match else 4


def score_place(
    place: dict,
    query: str | list[str],
    intents: set[str],
    selected_category: str,
    lat: float,
    lon: float,
    filters: dict | None = None,
) -> tuple[float, float]:
    filters = filters or {}
    distance = haversine_km(lat, lon, place["lat"], place["lon"])

    query_tokens = query if isinstance(query, list) else [
        token for token in normalize_text(query).split()
        if token not in STOP_WORDS["ru"] and len(token) > 2
    ]

    # Multi-field searchable text
    searchable_parts = [
        str(place.get("name", "")),
        str(place.get("name_kk", "")),
        str(place.get("name_en", "")),
        str(place.get("category", "")),
        str(place.get("category_label", "")),
        str(place.get("description", "")),
        str(place.get("description_kk", "")),
        str(place.get("description_en", "")),
        str(place.get("short_summary", "")),
        str(place.get("cuisine", "")),
    ]
    searchable = normalize_text(" ".join(searchable_parts))

    # 1. Simple lexical relevance
    lexical_score = 0.0
    for token in query_tokens:
        if token in normalize_text(place.get("name", "")):
            lexical_score += 4.0
        elif token in normalize_text(place.get("category_label", "")):
            lexical_score += 3.0
        elif token in searchable:
            lexical_score += 1.8

    category = str(place.get("category", ""))

    # 2. Intent matching
    intent_match = False
    if "cafe" in intents and category in {"cafe", "ice_cream"}:
        intent_match = True
    elif "park" in intents and category in {"park", "garden"}:
        intent_match = True
    elif "playground" in intents and (category in {"playground", "theme_park"} or place.get("kids_friendly")):
        intent_match = True
    elif "museum" in intents and category in {"museum", "gallery", "arts_centre"}:
        intent_match = True
    elif "attraction" in intents and category in {"attraction", "viewpoint", "monument", "memorial", "artwork"}:
        intent_match = True
    elif "restaurant" in intents and category in {"restaurant", "fast_food", "food_court"}:
        intent_match = True

    # 3. Context & Feature bonuses
    feature_bonus = 0.0
    if filters.get("accessibility") or "accessibility" in intents:
        feature_bonus += 3.5 if place.get("wheelchair") == "yes" else 0.0

    if filters.get("night") or "night" in intents:
        if category in {"bar", "pub", "cinema", "theatre"}:
            feature_bonus += 3.0

    if filters.get("group") or "group" in intents:
        if category in {"cafe", "park", "restaurant", "food_court", "theatre", "cinema", "mall", "sports_centre", "museum", "gallery", "pub", "bar"}:
            feature_bonus += 2.5
        capacity = place.get("capacity")
        if capacity is not None and capacity >= int(filters.get("group_size", 4)):
            feature_bonus += 4.0

    if filters.get("kids") or "playground" in intents:
        if category in {"playground", "theme_park", "zoo", "park", "garden", "museum"}:
            feature_bonus += 3.0

    if "cafe" in intents:
        if place.get("has_sockets"):
            feature_bonus += 2.5
        if place.get("is_quiet"):
            feature_bonus += 2.0

    # 4. Real-time diurnal context for Astana (UTC+5)
    astana_hour = get_astana_hour()
    if astana_hour >= 20 or astana_hour < 4:
        if category in {"bar", "pub"}:
            feature_bonus += 1.5
    elif 7 <= astana_hour <= 11:
        if category in {"cafe", "park"} or "breakfast" in searchable or "завтрак" in searchable:
            feature_bonus += 1.0

    selected_match = category_matches(selected_category, category)

    score = (
        lexical_score * 1.3
        + (3.5 if intent_match else 0.0)
        + (2.0 if selected_match else 0.0)
        + feature_bonus
        - distance * 0.75
    )
    return score, distance


def route_matrix(
    origin: tuple[float, float],
    places: list[dict],
    chain: bool = False,
    profile: str = "foot-walking",
) -> list[dict]:
    key = os.environ.get("ORS_API_KEY", "").strip()
    if not key or not places:
        return []
    coords = [[origin[1], origin[0]]] + [[item["lon"], item["lat"]] for item in places]
    payload = {
        "locations": coords,
        "sources": list(range(len(coords) - 1)) if chain else [0],
        "destinations": list(range(1, len(coords))),
        "metrics": ["distance", "duration"],
        "units": "m",
    }
    request = Request(
        f"https://api.openrouteservice.org/v2/matrix/{profile}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=12) as response:
            result = json.loads(response.read().decode("utf-8"))
        distances = result.get("distances", [])
        durations = result.get("durations", [])
        if chain:
            return [
                {
                    "distance_m": distances[index][index],
                    "duration_s": durations[index][index],
                }
                for index in range(min(len(places), len(distances), len(durations)))
                if len(distances[index]) > index and len(durations[index]) > index
            ]
        first_distances = distances[0] if distances else []
        first_durations = durations[0] if durations else []
        return [
            {"distance_m": first_distances[index], "duration_s": first_durations[index]}
            for index in range(min(len(places), len(first_distances), len(first_durations)))
        ]
    except Exception as error:
        print(f"OpenRouteService временно недоступен: {error}")
        return []


def route_geometry(
    origin: tuple[float, float],
    places: list[dict],
    profile: str = "foot-walking",
) -> list[list[float]] | None:
    """Return routed GeoJSON coordinates as [longitude, latitude] pairs."""
    key = os.environ.get("ORS_API_KEY", "").strip()
    if not key or not places:
        return None
    payload = {
        "coordinates": [[origin[1], origin[0]]] + [[item["lon"], item["lat"]] for item in places],
        "instructions": False,
        "elevation": False,
    }
    request = Request(
        f"https://api.openrouteservice.org/v2/directions/{profile}/geojson",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
        features = result.get("features") or []
        coordinates = features[0].get("geometry", {}).get("coordinates", []) if features else []
        if len(coordinates) < 2 or any(not isinstance(point, list) or len(point) < 2 for point in coordinates):
            return None
        return [[float(point[0]), float(point[1])] for point in coordinates]
    except Exception as error:
        print(f"OpenRouteService геометрия временно недоступна: {error}")
        return None


def synthesize_local_rag(
    place: dict,
    query: str,
    lang: str,
    mode: str,
    step_index: int = 1,
) -> tuple[str, str]:
    """Write a source-grounded reason and clearly framed idea for a visit."""
    lang = lang if lang in {"ru", "kk", "en"} else "ru"
    name = place.get(f"name_{lang}") or place.get("name", "")
    category_id = str(place.get("category", ""))
    category = localized_category_label(category_id, lang)
    description = place.get(f"description_{lang}") or (place.get("description") if lang == "ru" else "") or ""
    description = re.sub(r"\s+", " ", str(description or "")).strip()
    source_sentence = re.split(r"(?<=[.!?])\s+", description, maxsplit=1)[0] if description else ""
    normalized_query = normalize_text(query)
    intents = query_intents(query)
    wants_socket = any(term in normalized_query for term in ("розет", "socket", "outlet"))
    wants_wifi = any(term in normalized_query for term in ("wi-fi", "wifi", "интернет", "internet"))
    wants_quiet = any(term in normalized_query for term in ("тих", "quiet", "тиш", "calm", "шум", "тыныш"))
    wants_interactive = any(term in normalized_query for term in ("интерактив", "interactive"))
    group_requested = bool(place.get("group_requested")) or "group" in intents
    kids_requested = bool(place.get("kids_requested")) or "playground" in intents
    night_requested = bool(place.get("night_requested")) or "night" in intents
    access_requested = bool(place.get("accessibility_requested")) or "accessibility" in intents

    copy = {
        "ru": {
            "cafe_match": "Категория подходит под запрос о кофе.",
            "park_match": "Категория подходит под запрос на прогулку.",
            "kids_match": "Категория подходит для варианта с ребёнком.",
            "museum_match": "Категория культурного места соответствует запросу.",
            "attraction_match": "Категория соответствует запросу на необычное место.",
            "restaurant_match": "Категория соответствует запросу о еде.",
            "night_match": "Категория подходит для вечернего досуга.",
            "socket_yes": "В OSM отмечена розетка.",
            "socket_no": "В OSM отмечено отсутствие розетки.",
            "socket_unknown": "Наличие розетки в OSM не указано.",
            "wifi_yes": "В OSM отмечен Wi-Fi.",
            "wifi_no": "В OSM указано отсутствие Wi-Fi.",
            "wifi_unknown": "Наличие Wi-Fi в OSM не указано.",
            "quiet_yes": "В OSM отмечена тихая обстановка.",
            "quiet_no": "В OSM отмечена шумная обстановка.",
            "quiet_unknown": "Уровень шума в OSM не указан.",
            "child_limit": "Безопасность и интерактивная программа не подтверждены.",
            "interactive_unknown": "Интерактивная программа не указана в данных.",
            "night_limit": "Текущие часы и события не подтверждены.",
            "capacity_unknown": "Вместимость в OSM не указана.",
            "access_tag": "Для точки отмечен wheelchair=yes.",
            "access_route": "Путь рассчитан профилем wheelchair ORS; наземную доступность это не подтверждает.",
            "access_unknown": "Доступность пути профилем wheelchair не подтверждена.",
            "airport_limit": "Это POI категории «терминал»; досмотр и путь к гейту не учтены.",
            "capacity_suffix": "В OSM указана вместимость {capacity}; текущая доступность мест неизвестна.",
            "group_suffix": "Вместимость для группы из {size} человек не указана в OSM.",
            "cafe_quiet_action": " Уровень шума уточните перед визитом.",
            "interactive_action": " Перед визитом уточните, есть ли интерактивная программа.",
            "fallback": f"{name} — ближайшая точка категории «{category}».",
        },
        "kk": {
            "cafe_match": "Кофехана санаты кофе туралы сұрауға сәйкес.",
            "park_match": "Саябақ санаты серуен туралы сұрауға сәйкес.",
            "kids_match": "Санаты баламен бару нұсқасына сәйкес.",
            "museum_match": "Мәдени орын санаты сұрауға сәйкес.",
            "attraction_match": "Санаты ерекше орын туралы сұрауға сәйкес.",
            "restaurant_match": "Санаты тамақ туралы сұрауға сәйкес.",
            "night_match": "Санаты кешкі демалысқа сәйкес.",
            "socket_yes": "OSM-де розетка белгіленген.",
            "socket_no": "OSM-де розетканың жоқтығы белгіленген.",
            "socket_unknown": "OSM-де розетка туралы мәлімет жоқ.",
            "wifi_yes": "OSM-де Wi-Fi белгіленген.",
            "wifi_no": "OSM-де Wi-Fi жоқ деп көрсетілген.",
            "wifi_unknown": "OSM-де Wi-Fi туралы мәлімет жоқ.",
            "quiet_yes": "OSM-де тыныш орта белгіленген.",
            "quiet_no": "OSM-де шу деңгейі жоғары деп белгіленген.",
            "quiet_unknown": "OSM-де шу деңгейі көрсетілмеген.",
            "child_limit": "Қауіпсіздік пен интерактивті бағдарлама расталмаған.",
            "interactive_unknown": "Интерактивті бағдарлама деректерде көрсетілмеген.",
            "night_limit": "Қазіргі жұмыс уақыты мен оқиғалар расталмаған.",
            "capacity_unknown": "OSM-де сыйымдылық көрсетілмеген.",
            "access_tag": "Нысанға wheelchair=yes белгісі қойылған.",
            "access_route": "Жол ORS wheelchair профилімен есептелді; бұл жердегі қолжетімділікті растамайды.",
            "access_unknown": "Жолдың wheelchair профилімен қолжетімділігі расталмаған.",
            "airport_limit": "Бұл — әуежай терминалы санатындағы POI; тексеру мен қақпаға дейінгі жол есептелмеген.",
            "capacity_suffix": "OSM сыйымдылықты {capacity} деп көрсетеді; бос орын белгісіз.",
            "group_suffix": "OSM-де {size} адамдық топқа арналған сыйымдылық көрсетілмеген.",
            "cafe_quiet_action": " Бармас бұрын шу деңгейін нақтылаңыз.",
            "interactive_action": " Бармас бұрын интерактивті бағдарламаның бар-жоғын нақтылаңыз.",
            "fallback": f"{name} — жақын маңдағы «{category}» санатындағы нысан.",
        },
        "en": {
            "cafe_match": "The cafe category matches your coffee request.",
            "park_match": "The park category matches your walking request.",
            "kids_match": "The category fits a visit with children.",
            "museum_match": "The cultural venue category matches your request.",
            "attraction_match": "The category matches your request for an unusual place.",
            "restaurant_match": "The category matches your food request.",
            "night_match": "The category fits an evening outing.",
            "socket_yes": "OSM lists a power socket.",
            "socket_no": "OSM marks power sockets as unavailable.",
            "socket_unknown": "Power socket availability is not listed in OSM.",
            "wifi_yes": "OSM lists Wi-Fi.",
            "wifi_no": "OSM marks Wi-Fi as unavailable.",
            "wifi_unknown": "Wi-Fi availability is not listed in OSM.",
            "quiet_yes": "OSM marks the venue as quiet.",
            "quiet_no": "OSM marks the venue as noisy.",
            "quiet_unknown": "Noise level is not listed in OSM.",
            "child_limit": "Safety and interactive programming are unverified.",
            "interactive_unknown": "Interactive programming is not listed in the data.",
            "night_limit": "Current hours and events are unverified.",
            "capacity_unknown": "Capacity is not listed in OSM.",
            "access_tag": "The destination has a wheelchair=yes tag.",
            "access_route": "ORS returned a wheelchair-profile route; this does not confirm on-site access.",
            "access_unknown": "A wheelchair-profile route is not confirmed.",
            "airport_limit": "This is an airport-terminal POI; security time and gate distance are not included.",
            "capacity_suffix": "OSM lists capacity {capacity}; current seating availability is unknown.",
            "group_suffix": "OSM does not list capacity for a group of {size}.",
            "cafe_quiet_action": " Confirm noise levels before visiting.",
            "interactive_action": " Ask whether an interactive programme is available.",
            "fallback": f"{name} is a nearby POI in the {category} category.",
        },
    }[lang]

    reason_parts = []
    if "cafe" in intents and category_id in {"cafe", "ice_cream"}:
        reason_parts.append(copy["cafe_match"])
    elif kids_requested and category_id in {"playground", "theme_park", "zoo", "park", "garden", "museum"}:
        reason_parts.append(copy["kids_match"])
        reason_parts.append(copy["child_limit"])
    elif "park" in intents and category_id in {"park", "garden"}:
        reason_parts.append(copy["park_match"])
    elif "museum" in intents and category_id in {"museum", "gallery", "arts_centre"}:
        reason_parts.append(copy["museum_match"])
    elif "attraction" in intents and category_id in {"attraction", "viewpoint", "monument", "memorial", "artwork"}:
        reason_parts.append(copy["attraction_match"])
    elif "restaurant" in intents and category_id in {"restaurant", "fast_food", "food_court"}:
        reason_parts.append(copy["restaurant_match"])
    elif night_requested and category_id in {"bar", "pub", "cinema", "theatre"}:
        reason_parts.append(copy["night_match"])

    if category_id in {"cafe", "ice_cream"} and "cafe" in intents:
        if wants_socket:
            status = "socket_yes" if place.get("has_sockets") is True else "socket_no" if place.get("has_sockets") is False else "socket_unknown"
            reason_parts.append(copy[status])
        if wants_quiet:
            status = "quiet_yes" if place.get("is_quiet") is True else "quiet_no" if place.get("is_quiet") is False else "quiet_unknown"
            reason_parts.append(copy[status])
        if wants_wifi:
            status = "wifi_yes" if place.get("has_wifi") is True else "wifi_no" if place.get("has_wifi") is False else "wifi_unknown"
            reason_parts.append(copy[status])
    if wants_interactive and category_id in {"museum", "gallery", "arts_centre"}:
        reason_parts.append(copy["interactive_unknown"])
    if night_requested and category_id in {"bar", "pub", "cinema", "theatre"}:
        reason_parts.append(copy["night_limit"])
    if group_requested:
        capacity = place.get("capacity")
        size = int(place.get("group_size_requested") or parse_group_size(query))
        reason_parts.append(
            copy["capacity_suffix"].format(capacity=capacity)
            if capacity is not None
            else copy["group_suffix"].format(size=size)
        )
    if access_requested:
        if place.get("wheelchair") == "yes":
            reason_parts.append(copy["access_tag"])
        reason_parts.append(copy["access_route"] if place.get("route_accessibility_verified") else copy["access_unknown"])
    if category_id == "airport_terminal":
        reason_parts.append(copy["airport_limit"])

    if source_sentence and source_sentence not in reason_parts:
        reason_parts.append(source_sentence)
    elif not reason_parts:
        reason_parts.append(copy["fallback"])
    reason = " ".join(reason_parts)
    reason = reason[:280].rsplit(" ", 1)[0] + "…" if len(reason) > 280 else reason

    if mode == "mini_route":
        stop_words = {
            "ru": ["Начало", "Продолжение", "Завершение"],
            "kk": ["Бастау", "Жалғастыру", "Аяқтау"],
            "en": ["Start", "Continue", "Finish"],
        }[lang]
        role = stop_words[min(max(step_index - 1, 0), 2)]
        activity = {
            "ru": f"Идея маршрута · {role}: сделать эту точку одной из остановок прогулки.",
            "kk": f"Маршрут идеясы · {role}: бұл нүктені серуендегі аялдамалардың бірі ретінде қарастыру.",
            "en": f"Route idea · {role}: use this POI as one stop on the walk.",
        }[lang]
    else:
        activity_ideas = {
            "ru": {
                "airport_terminal": "Идея: остаться в общей зоне терминала; проход после досмотра, часы и путь к гейту уточните у аэропорта.",
                "cafe": "Идея: сделать паузу на кофе или чай; наличие Wi-Fi, розеток и часы уточните заранее.",
                "mall": "Идея: включить торговый центр в короткую прогулку; часы и доступные зоны проверьте перед визитом.",
                "museum": "Идея: заложить время на осмотр; текущую экспозицию и часы проверьте отдельно.",
                "gallery": "Идея: посмотреть выставочное пространство; актуальную программу уточните перед визитом.",
                "park": "Идея: пройтись по территории; проверьте погоду и доступность выбранного пути.",
                "garden": "Идея: сделать спокойную остановку на прогулке; проверьте режим посещения.",
                "viewpoint": "Идея: сделать короткую остановку ради вида; доступ на площадку уточните заранее.",
                "attraction": "Идея: включить объект в прогулку и осмотреть его на месте.",
                "playground": "Идея: рассмотреть точку для прогулки с ребёнком; проверьте состояние площадки и возрастные условия.",
                "theme_park": "Идея: рассмотреть точку для семейного визита; расписание и возрастные условия уточните заранее.",
                "bar": "Идея для вечернего визита; часы, правила входа и текущую программу проверьте отдельно.",
                "pub": "Идея для вечерней остановки; часы, правила входа и текущую программу проверьте отдельно.",
            },
            "kk": {
                "airport_terminal": "Идея: терминалдың ортақ аймағында қалу; тексеруден кейінгі өту тәртібі мен қақпаға дейінгі жолды әуежайдан нақтылаңыз.",
                "cafe": "Идея: кофе не шайға үзіліс жасау; Wi-Fi, розетка және жұмыс уақытын алдын ала нақтылаңыз.",
                "mall": "Идея: сауда орталығын қысқа серуенге қосу; жұмыс уақытын және қолжетімді аймақтарды тексеріңіз.",
                "museum": "Идея: аралауға уақыт бөлу; көрме мен жұмыс уақытын бөлек нақтылаңыз.",
                "gallery": "Идея: көрме кеңістігін көру; қазіргі бағдарламасын алдын ала нақтылаңыз.",
                "park": "Идея: аумақта серуендеу; ауа райы мен жолдың қолжетімділігін тексеріңіз.",
                "garden": "Идея: серуенде тыныш аялдама жасау; келу тәртібін тексеріңіз.",
                "viewpoint": "Идея: көрініс үшін қысқа аялдау; алаңға кіру мүмкіндігін нақтылаңыз.",
                "attraction": "Идея: нысанды серуенге қосып, барған жерде көру.",
                "playground": "Идея: баламен серуенге қарастыру; алаңның жағдайы мен жас шектеулерін тексеріңіз.",
                "theme_park": "Идея: отбасылық демалыс нүктесі ретінде қарастыру; кестесі мен жас шарттарын нақтылаңыз.",
                "bar": "Кешкі сапар идеясы; жұмыс уақытын, кіру ережесін және бағдарламасын тексеріңіз.",
                "pub": "Кешкі аялдама идеясы; жұмыс уақытын, кіру ережесін және бағдарламасын тексеріңіз.",
            },
            "en": {
                "airport_terminal": "Idea: stay in the public terminal area; check airport guidance for post-security access, hours, and gate distance.",
                "cafe": "Idea: pause for coffee or tea; check Wi-Fi, power outlets, and hours before visiting.",
                "mall": "Idea: include the mall in a short walk; confirm its hours and open areas first.",
                "museum": "Idea: set aside time to visit; check the current exhibition and opening hours.",
                "gallery": "Idea: visit the exhibition space; confirm the current programme before going.",
                "park": "Idea: take a walk through the area; check the weather and route access.",
                "garden": "Idea: make a quiet stop on the walk; confirm visitor hours.",
                "viewpoint": "Idea: stop for the view; confirm access to the viewpoint first.",
                "attraction": "Idea: add the site to your walk and explore it on arrival.",
                "playground": "Idea: consider it for a walk with children; check the condition and age guidance.",
                "theme_park": "Idea: consider it for a family visit; confirm schedule and age requirements.",
                "bar": "Evening visit idea; verify hours, entry rules, and current programme.",
                "pub": "Evening stop idea; verify hours, entry rules, and current programme.",
            },
        }
        activity = activity_ideas[lang].get(
            category_id,
            {
                "ru": "Идея: включить точку в прогулку; актуальные сведения и режим посещения уточните заранее.",
                "kk": "Идея: нүктені серуенге қосу; өзекті мәлімет пен келу уақытын алдын ала нақтылаңыз.",
                "en": "Idea: include this POI in your walk; confirm current details and visitor hours first.",
            }[lang],
        )
        if category_id in {"cafe", "ice_cream"} and wants_quiet:
            activity += copy["cafe_quiet_action"]
        if category_id in {"museum", "gallery", "arts_centre"} and wants_interactive:
            activity += copy["interactive_action"]

    return reason[:350], activity[:350]

def llm_prompt(query: str, candidates: list[dict], lang: str, mode: str) -> tuple[str, str]:
    evidence = []
    for idx, place in enumerate(candidates):
        evidence.append({
            "step": idx + 1,
            "id": place["id"],
            "name": place.get(f"name_{lang}") or place.get("name"),
            "category": place.get("category_label"),
            "description": place.get(f"description_{lang}") or place.get("description"),
            "has_sockets": place.get("has_sockets"),
            "is_night": place.get("is_night"),
            "kids_friendly": place.get("kids_friendly"),
            "wheelchair": place.get("wheelchair"),
            "distance_km": round(place["distance_km"], 2),
            "walk_minutes": place["walk_minutes"],
            "visit_minutes_estimate": [place["visit_minutes_min"], place["visit_minutes_max"]],
            "opening_hours": place.get("opening_hours") or None,
        })

    lang_instr = {
        "kk": "Жауапты қазақ тілінде бер.",
        "en": "Generate responses strictly in English.",
        "ru": "Формулируй ответ на русском языке.",
    }.get(lang, "Формулируй ответ на русском языке.")

    mode_instr = (
        "Пользователь запросил МИНИ-МАРШРУТ из 3 последовательных мест. "
        "В поле activity опиши роль точки в связном маршруте: Точка 1 (Старт), Точка 2 (Продолжение), Точка 3 (Завершение)."
        if mode == "mini_route"
        else "Пользователь выбирает отдельные рекомендации рядом."
    )

    hour = get_astana_hour()
    period = "ночь" if (hour >= 23 or hour < 6) else ("вечер" if hour >= 17 else ("утро" if hour < 12 else "день"))
    time_ctx = f"Текущее локальное время в Астане (UTC+5): {hour:02d}:00 ({period})."

    system = (
        "Ты — ИИ-помощник по прогулкам в Астане. "
        f"{lang_instr} {mode_instr} "
        f"{time_ctx} Не делай выводов о доступности места только по времени суток или категории. "
        "Используй как факты только поля переданного POI. Любые действия в activity формулируй как идею, а не как подтвержденную услугу или событие. "
        "Не придумывай рейтинги, события, удобства, расписание или характеристики. "
        "Никогда не утверждай уверенно, что место открыто прямо сейчас: напоминай уточнить часы перед визитом. "
        "Не выдумывай вымышленные адреса или историю. "
        "Верни строго JSON объект с ключом recommendations — массивом объектов с полями: "
        "id, reason (краткое 'почему подходит' по данным POI и расстоянию), "
        "activity (короткая идея для визита без неподтверждённых обещаний)."
    )
    user = json.dumps({"query": query[:500], "lang": lang, "mode": mode, "astana_time": f"{hour:02d}:00", "poi": evidence}, ensure_ascii=False)
    return system, user


def parse_llm_json(text: str) -> dict[str, dict]:
    try:
        # Extract json block if wrapped in markdown code fence
        clean = text.strip()
        if clean.startswith("```"):
            clean = re.sub(r"^```[a-z]*\n?", "", clean)
            clean = re.sub(r"\n?```$", "", clean)
        parsed = json.loads(clean.strip())
        return {
            str(item["id"]): {
                "reason": str(item.get("reason", "")).strip()[:350],
                "activity": str(item.get("activity", "")).strip()[:350],
            }
            for item in parsed.get("recommendations", [])
            if isinstance(item, dict) and item.get("id")
        }
    except Exception as e:
        print(f"Ошибка разбора LLM JSON: {e}")
        return {}


def call_gemini(query: str, candidates: list[dict], lang: str, mode: str) -> dict[str, dict]:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key or not candidates:
        return {}
    system, user = llm_prompt(query, candidates, lang, mode)
    prompt = system + "\n\nВходные данные JSON:\n" + user
    model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip() or "gemini-3.8-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    request = Request(
        url,
        data=json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.25},
        }).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return parse_llm_json(text)
    except Exception as error:
        print(f"Gemini API ({model}) недоступен: {error}")
        return {}


def call_openai_compatible(query: str, candidates: list[dict], lang: str, mode: str) -> dict[str, dict]:
    key = os.environ.get("OPENAI_API_KEY", "").strip() or os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key or not candidates:
        return {}
    base_url = os.environ.get("OPENAI_BASE_URL", "").strip()
    if not base_url:
        if os.environ.get("OPENAI_API_KEY", "").strip():
            base_url = "https://api.openai.com/v1/chat/completions"
        else:
            base_url = "https://api.deepseek.com/chat/completions"
    elif not base_url.endswith("/chat/completions"):
        base_url = base_url.rstrip("/") + "/chat/completions"

    deepseek_endpoint = "deepseek" in base_url.casefold()
    if deepseek_endpoint:
        model = os.environ.get("DEEPSEEK_MODEL", "").strip() or "deepseek-flash"
    elif "api.openai.com" in base_url.casefold():
        model = os.environ.get("OPENAI_MODEL", "").strip() or "gpt-5.6-luna"
    else:
        model = os.environ.get("OPENAI_MODEL", "").strip()
        if not model:
            print("Для OpenAI-совместимого сервиса нужно задать OPENAI_MODEL; используется локальный ответ.")
            return {}
    system, user = llm_prompt(query, candidates, lang, mode)
    request_body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }
    if model.startswith(("gpt-5.6-", "gpt-6-")):
        request_body.update({"reasoning_effort": "none", "max_completion_tokens": 700})
    else:
        request_body.update({"temperature": 0.25, "max_tokens": 700})
    request = Request(
        base_url,
        data=json.dumps(request_body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
        text = result["choices"][0]["message"]["content"]
        return parse_llm_json(text)
    except Exception as error:
        print(f"LLM API ({base_url}, {model}) недоступен: {error}")
        return {}


def call_deepseek(query: str, candidates: list[dict], lang: str, mode: str) -> dict[str, dict]:
    return call_openai_compatible(query, candidates, lang, mode)


def build_mini_route_timeline(
    origin: tuple[float, float],
    items: list[dict],
    segment_routes: list[dict] | None = None,
    routed_coordinates: list[list[float]] | None = None,
) -> dict:
    """Calculate sequenced walking route segments and total timeline."""
    if not items:
        return {}

    segments = []
    current_lat, current_lon = origin
    total_walk_min = 0
    total_distance_km = 0.0
    total_stay_min = 0

    for idx, place in enumerate(items):
        route = segment_routes[idx] if segment_routes and idx < len(segment_routes) else {}
        route_distance = route.get("distance_m")
        route_duration = route.get("duration_s")
        has_route = route_distance is not None and route_duration is not None
        dist_km = float(route_distance) / 1000 if has_route else haversine_km(current_lat, current_lon, place["lat"], place["lon"])
        walk_min = max(1, round(float(route_duration) / 60)) if has_route else max(1, round(dist_km * 1.35 / 0.075))
        stay_min = round((place["visit_minutes_min"] + place["visit_minutes_max"]) / 2)

        segments.append({
            "step": idx + 1,
            "from_point": "Ваша точка" if idx == 0 else items[idx - 1]["name"],
            "to_point": place["name"],
            "segment_distance_km": round(dist_km, 2),
            "segment_walk_minutes": walk_min,
            "stay_minutes": stay_min,
            "category": place.get("category_label", ""),
        })

        total_walk_min += walk_min
        total_distance_km += dist_km
        total_stay_min += stay_min
        current_lat, current_lon = place["lat"], place["lon"]

    route_points = (
        [[point[1], point[0]] for point in routed_coordinates]
        if routed_coordinates
        else [[origin[0], origin[1]]] + [[item["lat"], item["lon"]] for item in items]
    )
    line_coordinates = (
        routed_coordinates
        if routed_coordinates
        else [[origin[1], origin[0]]] + [[item["lon"], item["lat"]] for item in items]
    )
    geometry_source = "openrouteservice" if routed_coordinates else "schematic"

    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [origin[1], origin[0]]},
            "properties": {"title": "Старт (Ваша позиция)", "type": "origin", "step": 0},
        }
    ]
    for idx, item in enumerate(items):
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [item["lon"], item["lat"]]},
            "properties": {
                "title": item["name"],
                "step": idx + 1,
                "category": item.get("category_label", ""),
            },
        })
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": line_coordinates,
        },
        "properties": {
            "title": "Пешеходный мини-маршрут Qala Astana",
            "geometry_source": geometry_source,
        },
    })

    waypoints_str = "|".join(f"{it['lat']},{it['lon']}" for it in items[:-1])
    gmaps_route = (
        f"https://www.google.com/maps/dir/?api=1&origin={origin[0]},{origin[1]}"
        f"&destination={items[-1]['lat']},{items[-1]['lon']}"
        + (f"&waypoints={waypoints_str}" if waypoints_str else "")
        + "&travelmode=walking"
    )
    yandex_route = (
        "https://yandex.kz/maps/163/astana/?rtext="
        + "~".join(f"{p[0]}%2C{p[1]}" for p in route_points)
        + "&rtt=pd"
    )

    return {
        "total_distance_km": round(total_distance_km, 2),
        "total_walk_minutes": total_walk_min,
        "total_stay_minutes": total_stay_min,
        "total_duration_minutes": total_walk_min + total_stay_min,
        "segments": segments,
        "route_points": route_points,
        "geometry_source": geometry_source,
        "geojson": {
            "type": "FeatureCollection",
            "features": features,
        },
        "google_maps_route_url": gmaps_route,
        "yandex_maps_route_url": yandex_route,
    }


def recommend(payload: dict) -> dict:
    try:
        lat, lon = float(payload.get("lat")), float(payload.get("lon"))
    except (TypeError, ValueError):
        raise ValueError("Нужно выбрать точку на карте или разрешить геолокацию.")

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Координаты вне допустимого диапазона.")

    lang = str(payload.get("lang", "ru")).lower()
    if lang not in {"ru", "kk", "en"}:
        lang = "ru"

    mode = str(payload.get("mode", "standard")).lower()
    if mode not in {"standard", "mini_route"}:
        mode = "standard"

    # Demo coverage is split into separate city and airport regions.
    if not point_in_coverage(lat, lon):
        messages = {
            "ru": "Эта точка пока вне зоны собранных мест Астаны.",
            "kk": "Бұл нүкте әзірге Астананың қамтылған аймағынан тыс жерде.",
            "en": "This point is currently outside the Astana POI collection boundary.",
        }
        hints = {
            "ru": "Каталог охватывает центр, Expo, Mega Silk Way и отдельную зону аэропорта NQZ. Переместите точку в одну из этих зон.",
            "kk": "Каталог Астана орталығын, Expo, Mega Silk Way және NQZ әуежайының шағын аймағын қамтиды. Нүктені сол аймақтардың біріне жылжытыңыз.",
            "en": "The catalog covers central Astana, Expo, Mega Silk Way, and a separate NQZ airport area. Move the pin into one of those areas.",
        }
        return {
            "recommendations": [],
            "message": messages.get(lang, messages["ru"]),
            "hint": hints.get(lang, hints["ru"]),
            "generation_mode": LOCAL_GENERATOR,
            "routing_mode": "estimate",
            "lang": lang,
        }

    query = str(payload.get("query", "")).strip()[:500]
    selected_category = str(payload.get("category", "all"))
    try:
        radius_km = float(payload.get("radius_km", 5))
    except (TypeError, ValueError):
        radius_km = 5.0
    radius_km = min(MAX_DISTANCE_KM, max(0.5, radius_km))

    dataset = read_dataset()
    collected_areas = dataset.get("coverage_areas") or [
        {"id": "central_astana", "bbox": list(COVERAGE_AREAS["central_astana"])}
    ]
    if not any(
        area.get("bbox")
        and area["bbox"][0] <= lat <= area["bbox"][2]
        and area["bbox"][1] <= lon <= area["bbox"][3]
        for area in collected_areas
    ):
        message = {
            "ru": "Зона входит в план покрытия, но её POI ещё не загружены.",
            "kk": "Бұл аймақ қамту жоспарына кіреді, бірақ оның POI деректері әлі жүктелмеген.",
            "en": "This area is in the planned coverage, but its POIs have not been collected yet.",
        }
        hint = {
            "ru": "Нажмите «Обновить POI», чтобы собрать объекты NQZ из OpenStreetMap. До загрузки каталога рекомендации по аэропорту не формируются.",
            "kk": "OpenStreetMap деректерінен NQZ нысандарын жинау үшін «POI жаңарту» батырмасын басыңыз. Каталог жүктелгенше әуежай бойынша ұсыныс берілмейді.",
            "en": "Select “Refresh POIs” to collect NQZ objects from OpenStreetMap. Airport recommendations stay unavailable until that catalog is loaded.",
        }
        return {
            "recommendations": [],
            "message": message[lang],
            "hint": hint[lang],
            "generation_mode": LOCAL_GENERATOR,
            "routing_mode": "estimate",
            "lang": lang,
        }

    places = dataset.get("places", [])
    if not places:
        return {
            "recommendations": [],
            "message": "База POI пока пуста. Запустите сбор данных.",
            "hint": "Нажмите кнопку «Обновить POI» в шапке приложения.",
            "generation_mode": LOCAL_GENERATOR,
            "routing_mode": "estimate",
            "lang": lang,
        }

    intents = query_intents(query)
    group_requested = bool(payload.get("filter_group")) or "group" in intents
    group_size = parse_group_size(query, payload.get("group_size")) if group_requested else 4
    filters = {
        "accessibility": bool(payload.get("filter_accessibility")),
        "group": group_requested,
        "group_size": group_size,
        "night": bool(payload.get("filter_night")),
        "kids": bool(payload.get("filter_kids")),
    }

    # Tokenize query without stop words
    active_stop = STOP_WORDS.get(lang, STOP_WORDS["ru"]) | STOP_WORDS["ru"]
    query_tokens = [
        token for token in normalize_text(query).split()
        if token not in active_stop and len(token) > 2
    ]
    time_budget = parse_time_budget(query)

    scored = []
    for place in places:
        # Only explicit wheelchair=yes source tags qualify for accessibility requests.
        if (filters["accessibility"] or "accessibility" in intents) and place.get("wheelchair") != "yes":
            continue

        category = place.get("category", "")
        if filters["group"] and category not in {"cafe", "park", "restaurant", "food_court", "theatre", "cinema", "mall", "sports_centre", "museum", "gallery", "pub", "bar"}:
            continue
        capacity = place.get("capacity")
        if filters["group"] and capacity is not None and capacity < group_size:
            continue
        if filters["kids"] and category not in {"playground", "theme_park", "zoo", "park", "garden", "museum"}:
            continue
        if filters["night"] and category not in {"bar", "pub", "cinema", "theatre"}:
            continue

        if not category_matches(selected_category, place.get("category", "")):
            continue

        score, distance = score_place(place, query_tokens, intents, selected_category, lat, lon, filters)
        if (
            time_budget
            and time_budget["mode"] == "walk"
            and distance < 0.05
            and category != "airport_terminal"
        ):
            continue
        if distance <= radius_km:
            scored.append((score, distance, place))

    if not scored:
        empty_msg = {
            "ru": "В этой категории рядом мест не найдено. Попробуйте увеличить радиус поиска.",
            "kk": "Бұл санатта жақын маңнан орын табылмады. Іздеу радиусын үлкейтіп көріңіз.",
            "en": "No matching places found within this radius. Try increasing the search distance.",
        }
        access_hint = {
            "ru": "Фильтр доступности показывает только POI с явной отметкой wheelchair=yes в OpenStreetMap. В этом кэше таких подтверждённых отметок может не быть.",
            "kk": "Қолжетімділік сүзгісі OpenStreetMap-та wheelchair=yes белгісі бар нүктелерді ғана көрсетеді. Бұл кэште расталған белгі болмауы мүмкін.",
            "en": "The accessibility filter requires an explicit wheelchair=yes tag in OpenStreetMap; this cache may have no confirmed matches.",
        }
        return {
            "recommendations": [],
            "message": empty_msg.get(lang, empty_msg["ru"]),
            "hint": access_hint.get(lang, access_hint["ru"]) if filters["accessibility"] or "accessibility" in intents else "Увеличьте радиус или выберите категорию «Любая».",
            "generation_mode": LOCAL_GENERATOR,
            "routing_mode": "estimate",
            "lang": lang,
        }

    # Sort candidates
    scored.sort(key=lambda item: (-item[0], item[1]))

    # Deduplicate and pick diverse top 3
    selected_scored = []
    seen_categories = set()
    preferred_categories = set()
    for intent in intents:
        preferred_categories.update({
            "cafe": {"cafe", "ice_cream"},
            "park": {"park", "garden"},
            "playground": {"playground", "theme_park", "zoo", "park", "garden"},
            "museum": {"museum", "gallery", "arts_centre"},
            "attraction": {"attraction", "viewpoint", "monument", "memorial", "artwork"},
            "restaurant": {"restaurant", "fast_food", "food_court"},
        }.get(intent, set()))
    for candidate in scored:
        _, dist, place = candidate
        p_name = normalize_text(place.get("name", ""))
        p_cat = place.get("category")

        # Prefer a mix of nearby POI categories for general discovery and routes.
        if (mode == "mini_route" or selected_category == "all") and len(selected_scored) < 3:
            if p_cat in seen_categories and p_cat not in preferred_categories and len(scored) > 5 and len(seen_categories) < 3:
                continue

        duplicate = any(
            normalize_text(existing[2].get("name", "")) == p_name
            or haversine_km(place["lat"], place["lon"], existing[2]["lat"], existing[2]["lon"]) < 0.08
            for existing in selected_scored
        )
        if not duplicate:
            selected_scored.append(candidate)
            seen_categories.add(p_cat)
            if len(selected_scored) == 3:
                break

    # If mini_route was too strict on diversity, backfill
    if len(selected_scored) < 3:
        for candidate in scored:
            if candidate not in selected_scored:
                selected_scored.append(candidate)
                if len(selected_scored) == 3:
                    break

    selected = [item[2] for item in selected_scored]
    access_requested = filters["accessibility"] or "accessibility" in intents
    route_profile = "wheelchair" if access_requested else "foot-walking"
    routes = route_matrix((lat, lon), selected, chain=mode == "mini_route", profile=route_profile)
    routed_coordinates = (
        route_geometry((lat, lon), selected, profile=route_profile)
        if mode == "mini_route"
        else None
    )
    enriched = []
    for index, (score, distance, place) in enumerate(selected_scored):
        route = routes[index] if index < len(routes) else {}
        route_dist = route.get("distance_m")
        route_dur = route.get("duration_s")
        has_route = route_dist is not None and route_dur is not None

        disp_dist = float(route_dist) / 1000 if has_route else distance
        walk_mins = max(1, round(float(route_dur) / 60)) if has_route else max(1, round(distance * 1.35 / 0.075))
        visit_min, visit_max = VISIT_TIME_ESTIMATES.get(place.get("category", ""), (15, 30))

        synthesis_context = {
            **place,
            "group_requested": filters["group"],
            "group_size_requested": group_size if filters["group"] else None,
            "kids_requested": filters["kids"],
            "night_requested": filters["night"],
            "accessibility_requested": access_requested,
            "route_accessibility_verified": bool(
                access_requested and has_route and route_profile == "wheelchair"
            ),
        }
        reason, activity = synthesize_local_rag(
            synthesis_context,
            query,
            lang,
            mode,
            step_index=index + 1,
        )
        nav_links = make_navigation_links((lat, lon), (place["lat"], place["lon"]))
        group_capacity = place.get("capacity")
        group_capacity_verified = (
            bool(group_capacity is not None and group_capacity >= group_size)
            if filters["group"]
            else None
        )

        enriched.append({
            **place,
            "name": place.get(f"name_{lang}") or place.get("name"),
            "category_label": localized_category_label(str(place.get("category", "")), lang),
            "description": place.get(f"description_{lang}") or (place.get("description") if lang == "ru" else ""),
            "distance_km": disp_dist,
            "walk_minutes": walk_mins,
            "route_is_ors": has_route,
            "route_profile": route_profile if has_route else "estimate",
            "route_accessibility_verified": bool(access_requested and has_route and route_profile == "wheelchair"),
            "group_capacity": group_capacity,
            "group_capacity_source": place.get("capacity_source", ""),
            "group_capacity_verified": group_capacity_verified,
            "visit_minutes_min": visit_min,
            "visit_minutes_max": visit_max,
            "visit_time_is_estimate": True,
            "score": round(score, 2),
            "reason": reason,
            "activity": activity,
            "step_index": index + 1,
            "nav_links": nav_links,
            "twogis_url": nav_links["twogis_url"],
            "google_maps_url": nav_links["google_maps_url"],
            "yandex_maps_url": nav_links["yandex_maps_url"],
        })

    # Time budget evaluation
    time_constraint = None
    if time_budget:
        def fits(item: dict) -> bool:
            if time_budget["mode"] == "walk":
                return item["walk_minutes"] <= time_budget["minutes"]
            return item["walk_minutes"] + item["visit_minutes_max"] <= time_budget["minutes"]

        if mode == "mini_route":
            calculated_minutes = sum(item["walk_minutes"] for item in enriched)
            if time_budget["mode"] == "total":
                calculated_minutes += sum(item["visit_minutes_max"] for item in enriched)
            matched = calculated_minutes <= time_budget["minutes"]
        else:
            fitting = [item for item in enriched if fits(item)]
            if fitting:
                enriched = fitting
            calculated_minutes = max(
                (item["walk_minutes"] if time_budget["mode"] == "walk" else item["walk_minutes"] + item["visit_minutes_max"])
                for item in enriched
            ) if enriched else 0
            matched = bool(fitting)
        time_constraint = {
            **time_budget,
            "matched": matched,
            "calculated_minutes": calculated_minutes,
        }

    # External rewriting is opt-in for each request. The default stays local even
    # when a provider key exists in the environment.
    configured_provider = llm_provider()
    external_llm_requested = (
        payload.get("use_external_llm") is True
        and configured_provider in {"openai", "gemini", "deepseek"}
    )
    provider = configured_provider if external_llm_requested else LOCAL_GENERATOR
    llm_results = {}
    if provider == "gemini":
        llm_results = call_gemini(query, enriched, lang, mode)
    elif provider in {"openai", "deepseek"}:
        llm_results = call_openai_compatible(query, enriched, lang, mode)

    generation_mode = provider if llm_results else LOCAL_GENERATOR
    for item in enriched:
        gen = llm_results.get(item["id"])
        if gen and gen.get("reason"):
            item["reason"] = gen["reason"]
        if gen and gen.get("activity"):
            item["activity"] = gen["activity"]

    # Mini-route timeline metadata
    route_timeline = (
        build_mini_route_timeline((lat, lon), enriched, routes, routed_coordinates)
        if mode == "mini_route"
        else None
    )

    routing_enabled = bool(os.environ.get("ORS_API_KEY", "").strip())
    llm_privacy = {
        "ru": "Для запроса было разрешено внешнее переписывание: провайдер получает текст и выбранные POI." if external_llm_requested else "Внешняя модель этот запрос не получала.",
        "kk": "Сұрау үшін сыртқы өңдеуге рұқсат берілді: провайдер мәтін мен таңдалған POI деректерін алады." if external_llm_requested else "Сыртқы модель бұл сұрауды алған жоқ.",
        "en": "External rewriting was enabled for this request; the provider receives the query and selected POIs." if external_llm_requested else "The external model did not receive this request.",
    }
    privacy_notes = {
        "ru": (
            "Точка не сохраняется. OpenStreetMap получает тайлы видимой области карты; "
            + ("ORS получает координаты при расчёте маршрута. " if routing_enabled else "Расстояние оценивается локально. ")
            + llm_privacy["ru"]
        ),
        "kk": (
            "Нүкте сақталмайды. OpenStreetMap карта көрінісінің тайлдарын алады; "
            + ("маршрут есебінде ORS координаттарды алады. " if routing_enabled else "қашықтық жергілікті түрде бағаланады. ")
            + llm_privacy["kk"]
        ),
        "en": (
            "The point is not stored. OpenStreetMap receives tiles for the visible map area; "
            + ("ORS receives coordinates when routing. " if routing_enabled else "distance is estimated locally. ")
            + llm_privacy["en"]
        ),
    }

    airport_bounds = COVERAGE_AREAS.get("nqz_airport")
    in_airport_area = bool(
        airport_bounds
        and airport_bounds[0] <= lat <= airport_bounds[2]
        and airport_bounds[1] <= lon <= airport_bounds[3]
    )
    flight_query = bool(re.search(r"аэропорт|вылет|рейс|посадк|flight|airport|boarding", query, re.IGNORECASE))
    context_note = None
    if in_airport_area or flight_query:
        context_note = {
            "ru": "Перед рейсом: каталог не знает досмотр, очередь, выход к гейту и время посадки. Не используйте оценку прогулки как гарантию, что вы успеете на рейс.",
            "kk": "Ұшу алдында: каталог тексеру уақытын, кезекті, қақпаға дейінгі жолды және отырғызу уақытын білмейді. Серуен бағасын рейске үлгеру кепілі деп қабылдамаңыз.",
            "en": "Before a flight: the catalog does not know security queues, gate distance, or boarding time. Do not treat a walk estimate as a guarantee that you will make your flight.",
        }.get(lang)

    group_planning = None
    if filters["group"]:
        verified = sum(item.get("group_capacity_verified") is True for item in enriched)
        unknown = sum(item.get("group_capacity_verified") is None for item in enriched)
        group_planning = {
            "party_size": group_size,
            "capacity_verified_count": verified,
            "capacity_unknown_count": unknown,
            "note": {
                "ru": "Подбор предпочитает подходящие типы мест. Вместимость подтверждена только там, где указана в OSM; при отсутствии тега она неизвестна.",
                "kk": "Іріктеу топқа ыңғайлы орын санаттарын басым қояды. Сыйымдылық тек OSM-де көрсетілгенде расталады; белгі болмаса, ол белгісіз.",
                "en": "Results prefer group-suitable place types. Capacity is confirmed only when OSM provides a value; otherwise it is unknown.",
            }.get(lang),
        }

    accessibility_note = None
    if access_requested:
        has_wheelchair_route = bool(enriched) and all(item.get("route_accessibility_verified") for item in enriched)
        accessibility_note = {
            "ru": "Отметка wheelchair=yes относится к точке. Пешеходный маршрут проверен профилем wheelchair OpenRouteService." if has_wheelchair_route else "Отметка wheelchair=yes относится только к точке. Путь до неё не подтверждён как доступный для кресла-коляски.",
            "kk": "wheelchair=yes белгісі орынның өзіне қатысты. Жаяу бағыт OpenRouteService wheelchair профилімен тексерілді." if has_wheelchair_route else "wheelchair=yes белгісі тек орынға қатысты. Оған дейінгі жолдың арбаға қолжетімділігі расталмаған.",
            "en": "The wheelchair=yes tag describes the destination. The walk was checked with OpenRouteService's wheelchair profile." if has_wheelchair_route else "The wheelchair=yes tag describes the destination only. The route to it is not confirmed wheelchair accessible.",
        }.get(lang)

    return {
        "recommendations": enriched,
        "is_mini_route": mode == "mini_route",
        "route_summary": route_timeline,
        "message": "",
        "generation_mode": generation_mode,
        "routing_mode": "openrouteservice" if any(item["route_is_ors"] for item in enriched) else "estimate",
        "time_constraint": time_constraint,
        "privacy_note": privacy_notes.get(lang, privacy_notes["ru"]),
        "external_llm_requested": external_llm_requested,
        "external_llm_provider": configured_provider if external_llm_requested else "",
        "context_note": context_note,
        "group_planning": group_planning,
        "accessibility_note": accessibility_note,
        "lang": lang,
    }


def get_openapi_spec() -> dict:
    """Standard OpenAPI 3.0.3 specification for hackathon jury and API consumers."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Qala Astana 2.0 API",
            "version": "2.0.0",
            "description": "AI-Powered RAG City Walk Recommendation Engine for Build with AI Track 1 (НИЦ Smart City & GDG Astana).",
            "contact": {"name": "Qala Astana Core Team"},
        },
        "servers": [{"url": f"http://{HOST}:{PORT}", "description": "Local Engine Server"}],
        "paths": {
            "/api/status": {
                "get": {
                    "summary": "Engine & Dataset Status",
                    "responses": {"200": {"description": "Status, POI count, configured optional LLM provider, local default generator, and stretch goals"}},
                }
            },
            "/api/health": {
                "get": {
                    "summary": "Health Telemetry & Category Breakdown",
                    "responses": {"200": {"description": "Detailed uptime, Astana local time, and category distribution"}},
                }
            },
            "/api/places": {
                "get": {
                    "summary": "Astana POI Catalog",
                    "responses": {"200": {"description": "Full collection of enriched POIs within Astana urban bounds"}},
                }
            },
            "/api/recommend": {
                "post": {
                    "summary": "Generate RAG Recommendations or Mini-Route",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["lat", "lon"],
                                    "properties": {
                                        "lat": {"type": "number", "example": 51.1283},
                                        "lon": {"type": "number", "example": 71.4305},
                                        "query": {"type": "string", "example": "Хочу тихий кофе с розеткой на полчаса"},
                                        "category": {"type": "string", "example": "cafe"},
                                        "radius_km": {"type": "number", "example": 3.0},
                                        "mode": {"type": "string", "enum": ["standard", "mini_route"], "default": "standard"},
                                        "lang": {"type": "string", "enum": ["ru", "kk", "en"], "default": "ru"},
                                        "filter_accessibility": {"type": "boolean"},
                                        "filter_group": {"type": "boolean"},
                                        "filter_night": {"type": "boolean"},
                                        "filter_kids": {"type": "boolean"},
                                        "use_external_llm": {"type": "boolean", "default": False, "description": "Explicit per-request consent to send the prompt and selected POI context to the configured external model. The user's separate GPS coordinates are omitted."},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "1-3 grounded recommendations with walk durations, motivations, activities, and map deep links"},
                        "400": {"description": "Validation error"},
                        "429": {"description": "Rate limit exceeded (120 req/min)"},
                    },
                }
            },
            "/api/sync": {
                "post": {
                    "summary": "Trigger Overpass Background Sync",
                    "responses": {"202": {"description": "Sync worker launched"}},
                }
            },
        },
    }


def get_docs_html() -> str:
    """Render a standalone, offline Material 3 dark API documentation page."""
    return """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Qala Astana 2.0 — API Reference</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto+Mono:wght@400;500&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #121316;
      --surface: #1e1f25;
      --surface-high: #282a33;
      --primary: #a8c7fa;
      --on-primary: #042f65;
      --text: #e2e2e9;
      --text-dim: #92909a;
      --method-get: #81c995;
      --method-post: #a8c7fa;
      --border: #333540;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Google Sans', 'Roboto', sans-serif; background: var(--bg); color: var(--text); padding: 32px 20px; line-height: 1.5; }
    .container { max-width: 960px; margin: 0 auto; }
    header { margin-bottom: 32px; border-bottom: 1px solid var(--border); padding-bottom: 24px; }
    h1 { font-size: 28px; font-weight: 700; color: #fff; margin-bottom: 8px; }
    p.sub { color: var(--text-dim); font-size: 15px; margin-bottom: 16px; }
    .chips { display: flex; gap: 8px; flex-wrap: wrap; }
    .chip { background: var(--surface-high); padding: 4px 12px; border-radius: 999px; font-size: 12px; color: var(--primary); font-weight: 500; }
    .endpoint { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; margin-bottom: 20px; padding: 20px; transition: border-color .2s; }
    .endpoint:hover { border-color: var(--primary); }
    .ep-head { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
    .badge { font-family: 'Roboto Mono', monospace; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 8px; text-transform: uppercase; }
    .badge.get { background: rgba(129, 201, 149, 0.2); color: var(--method-get); }
    .badge.post { background: rgba(168, 199, 250, 0.2); color: var(--method-post); }
    .path { font-family: 'Roboto Mono', monospace; font-size: 16px; font-weight: 500; color: #fff; }
    .desc { font-size: 14px; color: var(--text-dim); margin-bottom: 14px; }
    pre { background: #0b0c0e; border: 1px solid var(--border); border-radius: 12px; padding: 14px; font-family: 'Roboto Mono', monospace; font-size: 13px; color: #c3ecf6; overflow-x: auto; margin-top: 8px; }
    a.link { color: var(--primary); text-decoration: none; }
    a.link:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Qala Astana 2.0 API Reference</h1>
      <p class="sub">AI-Powered City Walk RAG Architecture for Build with AI Hackathon (Track 1 — НИЦ Smart City & GDG Astana).</p>
      <div class="chips">
        <span class="chip">OpenAPI 3.0.3</span>
        <span class="chip">REST & JSON UTF-8</span>
        <span class="chip">CORS Enabled</span>
        <span class="chip">Rate Limit: 120 req/min</span>
        <span class="chip">821 Astana POIs</span>
        <a class="chip link" href="/api/openapi.json" target="_blank">View raw openapi.json</a>
        <a class="chip link" href="/" target="_blank">Open Web Client</a>
      </div>
    </header>

    <div class="endpoint">
      <div class="ep-head">
        <span class="badge get">GET</span>
        <span class="path">/api/status</span>
      </div>
      <div class="desc">Возвращает статус готовности базы POI, время синхронизации, активный LLM провайдер и список stretch-goals.</div>
      <pre>curl -s http://127.0.0.1:8765/api/status</pre>
    </div>

    <div class="endpoint">
      <div class="ep-head">
        <span class="badge get">GET</span>
        <span class="path">/api/health</span>
      </div>
      <div class="desc">Детальная телеметрия: аптайм сервера, локальное время Астаны (UTC+5), распределение 821 POI по категориям и состояние in-memory кэша.</div>
      <pre>curl -s http://127.0.0.1:8765/api/health</pre>
    </div>

    <div class="endpoint">
      <div class="ep-head">
        <span class="badge get">GET</span>
        <span class="path">/api/places</span>
      </div>
      <div class="desc">Полный каталог собранных мест для рендеринга кластеров на карте Leaflet или в сторонних гео-системах.</div>
      <pre>curl -s http://127.0.0.1:8765/api/places</pre>
    </div>

    <div class="endpoint">
      <div class="ep-head">
        <span class="badge post">POST</span>
        <span class="path">/api/recommend</span>
      </div>
      <div class="desc">Поиск по OpenStreetMap по словам и интентам, отбор по расстоянию, затем генерация краткой идеи для визита. Поддерживает одиночный режим и мини-маршрут из трёх POI; время пути оценивается по расстоянию либо рассчитывается OpenRouteService, если ключ настроен.</div>
      <pre>curl -X POST http://127.0.0.1:8765/api/recommend \\
  -H "Content-Type: application/json" \\
  -d '{"lat": 51.1283, "lon": 71.4305, "query": "Хочу тихий кофе с розеткой на полчаса", "category": "cafe", "lang": "ru"}'</pre>
    </div>

    <div class="endpoint">
      <div class="ep-head">
        <span class="badge post">POST</span>
        <span class="path">/api/sync</span>
      </div>
      <div class="desc">Запуск фонового обновления объектов через OpenStreetMap Overpass API в границах Астаны.</div>
      <pre>curl -X POST http://127.0.0.1:8765/api/sync</pre>
    </div>
  </div>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "QalaAstana/2.0"

    def address_string(self) -> str:
        return str(self.client_address[0])

    def log_message(self, format: str, *args) -> None:
        print(f"{self.client_address[0]} - {format % args}", flush=True)

    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, status: int, html_text: str) -> None:
        body = html_text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, name: str, attachment_name: str | None = None) -> None:
        file_path = ROOT / name
        if not file_path.is_file():
            self.send_error(404)
            return
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".svg": "image/svg+xml",
            ".webp": "image/webp",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        }.get(file_path.suffix, "application/octet-stream")
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        if attachment_name:
            self.send_header("Content-Disposition", f'attachment; filename="{attachment_name}"')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:
        client_ip = self.client_address[0]
        path = urlparse(self.path).path

        if path.startswith("/api/") and not check_rate_limit(client_ip):
            self.send_json(429, {"error": "Слишком много запросов. Подождите минуту (Rate limit: 120 req/min)."})
            return

        if path == "/api/status":
            self.send_json(200, get_status())
        elif path == "/api/health":
            self.send_json(200, get_health())
        elif path == "/api/openapi.json":
            self.send_json(200, get_openapi_spec())
        elif path == "/api/docs":
            self.send_html(200, get_docs_html())
        elif path == "/api/places":
            data = read_dataset()
            self.send_json(200, {
                "places": data.get("places", []),
                "updated_at": data.get("updated_at", ""),
                "last_attempt_at": data.get("last_attempt_at", ""),
                "collection_status": data.get("collection_status", "legacy_cache"),
                "source": data.get("source", "OpenStreetMap (Overpass)"),
            })
        elif path == "/":
            self.serve_file("index.html")
        elif path in {"/styles.css", "/app.js"}:
            self.serve_file(path.lstrip("/"))
        elif path in {"/presentation", "/presentation.html"}:
            self.serve_file("presentation.html")
        elif path == "/output/Qala_Astana_Case1_Final.pptx":
            self.serve_file("output/Qala_Astana_Case1_Final.pptx", "Qala_Astana_Case1_Final.pptx")
        elif path == "/output/Qala_Astana_Case1_Preview.webp":
            self.serve_file("output/Qala_Astana_Case1_Preview.webp")
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip):
            self.send_json(429, {"error": "Слишком много запросов. Подождите минуту (Rate limit: 120 req/min)."})
            return

        path = urlparse(self.path).path
        if path == "/api/sync":
            started = start_sync(force=True)
            self.send_json(202, {"started": started, "syncing": SYNC_STATE["syncing"]})
            return
        if path != "/api/recommend":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 100_000:
                self.send_json(413, {"error": "Запрос слишком большой."})
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = recommend(payload)
            self.send_json(200, result)
        except ValueError as error:
            self.send_json(400, {"error": str(error)})
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "Не удалось прочитать запрос."})
        except Exception as error:
            print(f"Ошибка обработки запроса: {error}")
            self.send_json(500, {"error": "Не удалось собрать рекомендации. Попробуйте ещё раз."})


def main() -> None:
    load_dotenv()
    start_sync()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Qala Astana 2.0 запущен: http://{HOST}:{PORT}")
    print("Остановка: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
