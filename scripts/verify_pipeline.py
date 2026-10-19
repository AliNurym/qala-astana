import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import server

sys.stdout.reconfigure(encoding="utf-8")

print("=== 1. Mega Silk Way (30-60 min) ===")
res1 = server.recommend({
    "lat": 51.0891, "lon": 71.4073,
    "query": "Я сейчас возле Mega Silk Way, хочу прогуляться 30-60 минут",
    "category": "all", "radius_km": 2.0
})
print("Found:", len(res1["recommendations"]))
for p in res1["recommendations"]:
    print(f"  • {p['name']} ({p.get('category_label')}): {p['distance_km']*1000:.0f}m, пешком: {p['walk_minutes']} мин. Рейтинг: ⭐{p.get('rating')}")
    print(f"    Почему: {p['reason'][:90]}...")
    print(f"    Что сделать: {p['activity'][:90]}...")

print("\n=== 2. Quiet Cafe with Socket ===")
res2 = server.recommend({
    "lat": 51.1352, "lon": 71.4241,
    "query": "Хочу тихое место с кофе и розеткой",
    "category": "cafe", "radius_km": 2.0
})
print("Found:", len(res2["recommendations"]))
for p in res2["recommendations"]:
    print(f"  • {p['name']}: Розетки={p.get('has_sockets')}, Wi-Fi={p.get('has_wifi')}, Тишина={p.get('is_quiet')}")
    print(f"    Что сделать: {p['activity']}")

print("\n=== 3. Mini-Route Mode (3-stop sequenced itinerary) ===")
res3 = server.recommend({
    "lat": 51.1283, "lon": 71.4305,
    "query": "Построй мини-маршрут на 1-2 часа",
    "category": "all", "mode": "mini_route"
})
print("Is mini-route:", res3["is_mini_route"])
s = res3.get("route_summary")
if s:
    print(f"Общий хронометраж: {s['total_duration_minutes']} мин (Пешком: {s['total_walk_minutes']} мин / {s['total_distance_km']} км, на точках: {s['total_stay_minutes']} мин)")
    for seg in s["segments"]:
        print(f"  Шаг {seg['step']}: {seg['from_point']} -> {seg['to_point']} (пешком {seg['segment_walk_minutes']} мин, на месте ~{seg['stay_minutes']} мин)")
for p in res3["recommendations"]:
    print(f"  - Точка {p['step_index']}: {p['name']} -> {p['activity']}")

print("\n=== 4. Multilingual (Kazakh) ===")
res4 = server.recommend({
    "lat": 51.0898, "lon": 71.4147,
    "query": "Экспо қалашығындағы серуен",
    "category": "all", "lang": "kk"
})
first = res4["recommendations"][0]
print(f"Атауы (KZ): {first['name']}")
print(f"Себебі (KZ): {first['reason']}")
print(f"Әрекет (KZ): {first['activity']}")

print("\n=== 5. Airport Coverage Boundary ===")
res5 = server.recommend({
    "lat": 51.0250, "lon": 71.4650,
    "query": "У меня 2 часа перед вылетом в аэропорту",
    "category": "all"
})
print("Сообщение:", res5["message"])
print("Подсказка:", res5["hint"])

print("\n=== 6. Night Activity & Group ===")
res6 = server.recommend({
    "lat": 51.0872, "lon": 71.4180,
    "query": "Ночная активность для компании из 4 человек",
    "category": "all",
    "filter_night": True,
    "filter_group": True
})
print("Found night/group:", len(res6["recommendations"]))
for p in res6["recommendations"]:
    print(f"  • {p['name']}: Ночь={p.get('is_night')}, Группа={p.get('is_group_friendly')}, Часы={p.get('opening_hours')}")
