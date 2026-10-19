import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import server
from osm_data import category_for, derive_features, normalize_element, short_summary


def place(identifier, name, category, lat_offset=0.001, lon_offset=0.001):
    return {
        "id": "node/" + identifier,
        "name": name,
        "lat": 51.1283 + lat_offset,
        "lon": 71.4305 + lon_offset,
        "category": category,
        "category_label": category,
        "description": "",
        "opening_hours": "",
        "source_url": "https://www.openstreetmap.org/node/" + identifier,
    }


class TimeBudgetTests(unittest.TestCase):
    def test_walk_time_range_uses_upper_limit(self):
        self.assertEqual(
            server.parse_time_budget("Хочу прогуляться 30–60 минут"),
            {"minutes": 60, "mode": "walk"},
        )

    def test_total_time_budget_accepts_word_numbers(self):
        self.assertEqual(
            server.parse_time_budget("У меня два часа перед вылетом"),
            {"minutes": 120, "mode": "total"},
        )

    def test_last_couple_of_hours_is_recognized_as_total_time(self):
        self.assertEqual(
            server.parse_time_budget("Ищу необычную ночную активность (последние пару часов)"),
            {"minutes": 120, "mode": "total"},
        )

    def test_half_hour_is_recognized(self):
        self.assertEqual(
            server.parse_time_budget("У меня полчаса, куда рядом?"),
            {"minutes": 30, "mode": "total"},
        )

    def test_missing_duration_is_not_inferred(self):
        self.assertIsNone(server.parse_time_budget("Хочу выпить кофе рядом"))


class IntentTests(unittest.TestCase):
    def test_common_verb_does_not_trigger_child_filter_intent(self):
        intents = server.query_intents("Хочу прогуляться и увидеть что-нибудь интересное")
        self.assertIn("park", intents)
        self.assertIn("attraction", intents)
        self.assertNotIn("playground", intents)

    def test_child_words_do_trigger_playground_intent(self):
        self.assertIn("playground", server.query_intents("Ищу место с ребёнком и площадкой"))

    def test_common_category_word_does_not_outrank_a_much_closer_place(self):
        query = "Хочу кофе поблизости"
        intents = server.query_intents(query)
        nearby = place("near", "Кофейня", "cafe", 0.001, 0.001)
        farther = place("far", "Кофе и Часы", "cafe", 0.001, 0.04)
        nearby_score, _ = server.score_place(nearby, query, intents, "cafe", 51.1283, 71.4305)
        farther_score, _ = server.score_place(farther, query, intents, "cafe", 51.1283, 71.4305)
        self.assertGreater(nearby_score, farther_score)


class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.places = [
            place("1", "Кофейня рядом", "cafe"),
            place("2", "Городской парк", "park", 0.003, 0.002),
            place("3", "Музей", "museum", 0.004, 0.004),
            place("4", "Ресторан", "restaurant", 0.005, 0.005),
        ]
        self.dataset = {"places": self.places}
        self.dataset_patch = patch.object(server, "read_dataset", return_value=self.dataset)
        self.route_patch = patch.object(server, "route_matrix", return_value=[])
        self.provider_patch = patch.object(server, "llm_provider", return_value="demo")
        self.dataset_patch.start()
        self.route_patch.start()
        self.provider_patch.start()
        self.addCleanup(self.dataset_patch.stop)
        self.addCleanup(self.route_patch.stop)
        self.addCleanup(self.provider_patch.stop)

    def request(self, **overrides):
        payload = {
            "lat": 51.1283,
            "lon": 71.4305,
            "query": "Хочу найти место рядом",
            "category": "all",
            "radius_km": 5,
        }
        payload.update(overrides)
        return server.recommend(payload)

    def test_returns_at_most_three_with_visit_time_estimate(self):
        result = self.request()
        self.assertLessEqual(len(result["recommendations"]), 3)
        self.assertTrue(all(item["visit_time_is_estimate"] for item in result["recommendations"]))
        self.assertTrue(all(item["visit_minutes_min"] <= item["visit_minutes_max"] for item in result["recommendations"]))

    def test_external_model_is_not_called_without_explicit_opt_in(self):
        with patch.object(server, "llm_provider", return_value="deepseek"), patch.object(server, "call_openai_compatible") as external_call:
            result = self.request()
        external_call.assert_not_called()
        self.assertFalse(result["external_llm_requested"])
        self.assertEqual(result["generation_mode"], server.LOCAL_GENERATOR)

    def test_external_model_requires_boolean_opt_in(self):
        with patch.object(server, "llm_provider", return_value="deepseek"), patch.object(server, "call_openai_compatible") as external_call:
            result = self.request(use_external_llm="true")
        external_call.assert_not_called()
        self.assertFalse(result["external_llm_requested"])

    def test_external_model_runs_only_for_explicit_opt_in(self):
        with patch.object(server, "llm_provider", return_value="deepseek"), patch.object(server, "call_openai_compatible", return_value={}) as external_call:
            result = self.request(use_external_llm=True, lang="en")
        external_call.assert_called_once()
        self.assertTrue(result["external_llm_requested"])
        self.assertEqual(result["external_llm_provider"], "deepseek")
        self.assertIn("External rewriting", result["privacy_note"])

    def test_external_llm_prompt_omits_structured_gps_coordinates(self):
        candidate = place("gps-check", "Кафе рядом", "cafe")
        candidate.update({
            "distance_km": 0.3,
            "walk_minutes": 5,
            "visit_minutes_min": 20,
            "visit_minutes_max": 40,
            "name_ru": "Кафе рядом",
            "category_label": "Кафе",
            "description": "",
        })
        _, user_prompt = server.llm_prompt("Найди кафе рядом", [candidate], "ru", "standard")
        self.assertNotIn('"lat"', user_prompt)
        self.assertNotIn('"lon"', user_prompt)

    def test_local_reason_uses_socket_and_quietness_evidence_from_the_query(self):
        self.places[0].update({"has_sockets": True, "is_quiet": None})
        result = self.request(query="Хочу тихое кафе с розеткой", category="cafe")
        reason = result["recommendations"][0]["reason"].lower()
        self.assertIn("кофе", reason)
        self.assertIn("розетка", reason)
        self.assertIn("шум", reason)
        self.assertIn("не указан", reason)

    def test_local_reason_does_not_invent_interactive_kids_programming(self):
        result = self.request(
            query="Еду с ребёнком — хочу музей с интерактивом",
            category="museum",
        )
        reason = result["recommendations"][0]["reason"].lower()
        activity = result["recommendations"][0]["activity"].lower()
        self.assertIn("ребён", reason)
        self.assertIn("интерактивная программа не указана", reason)
        self.assertIn("уточните", activity)

    def test_chat_provider_uses_current_openai_payload(self):
        candidate = {
            "id": "node/test", "name": "Cafe", "category_label": "Cafe",
            "distance_km": 0.3, "walk_minutes": 5,
            "visit_minutes_min": 20, "visit_minutes_max": 40,
        }
        response = MagicMock()
        response.__enter__.return_value.read.return_value = (
            b'{"choices":[{"message":{"content":"{\\"recommendations\\":[]}"}}]}'
        )
        with patch.dict("os.environ", {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "",
            "OPENAI_MODEL": "",
            "DEEPSEEK_API_KEY": "",
            "DEEPSEEK_MODEL": "",
        }, clear=True), patch.object(server, "urlopen", return_value=response) as mocked_urlopen:
            server.call_openai_compatible("coffee", [candidate], "en", "standard")
        request = mocked_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "gpt-5.6-luna")
        self.assertEqual(payload["reasoning_effort"], "none")
        self.assertEqual(payload["max_completion_tokens"], 700)
        self.assertNotIn("temperature", payload)

    def test_deepseek_model_does_not_inherit_openai_model_setting(self):
        candidate = {
            "id": "node/test", "name": "Cafe", "category_label": "Cafe",
            "distance_km": 0.3, "walk_minutes": 5,
            "visit_minutes_min": 20, "visit_minutes_max": 40,
        }
        response = MagicMock()
        response.__enter__.return_value.read.return_value = (
            b'{"choices":[{"message":{"content":"{\\"recommendations\\":[]}"}}]}'
        )
        with patch.dict("os.environ", {
            "OPENAI_API_KEY": "",
            "OPENAI_BASE_URL": "",
            "OPENAI_MODEL": "gpt-5.6-luna",
            "DEEPSEEK_API_KEY": "test-key",
            "DEEPSEEK_MODEL": "deepseek-flash",
        }, clear=True), patch.object(server, "urlopen", return_value=response) as mocked_urlopen:
            server.call_openai_compatible("coffee", [candidate], "en", "standard")
        request = mocked_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "deepseek-flash")
        self.assertEqual(payload["max_tokens"], 700)
        self.assertIn("temperature", payload)

    def test_gemini_uses_configured_default_model_without_live_api_call(self):
        candidate = {
            "id": "node/test", "name": "Cafe", "category_label": "Cafe",
            "distance_km": 0.3, "walk_minutes": 5,
            "visit_minutes_min": 20, "visit_minutes_max": 40,
        }
        response = MagicMock()
        response.__enter__.return_value.read.return_value = (
            b'{"candidates":[{"content":{"parts":[{"text":"{\\"recommendations\\":[]}"}]}}]}'
        )
        with patch.dict("os.environ", {
            "GEMINI_API_KEY": "test-key",
            "GEMINI_MODEL": "",
        }, clear=True), patch.object(server, "urlopen", return_value=response) as mocked_urlopen:
            server.call_gemini("coffee", [candidate], "en", "standard")
        request = mocked_urlopen.call_args.args[0]
        self.assertIn("/models/gemini-3.8-flash:generateContent", request.full_url)
        self.assertEqual(request.get_header("X-goog-api-key"), "test-key")

    def test_category_filter_is_applied(self):
        result = self.request(category="cafe")
        self.assertTrue(result["recommendations"])
        self.assertTrue(all(item["category"] == "cafe" for item in result["recommendations"]))

    def test_radius_excludes_far_results(self):
        result = self.request(radius_km=0.5)
        self.assertTrue(all(item["distance_km"] <= 0.5 for item in result["recommendations"]))

    def test_time_budget_is_returned_as_an_estimate(self):
        result = self.request(query="У меня 30 минут, куда рядом сходить?")
        self.assertEqual(result["time_constraint"]["minutes"], 30)
        self.assertEqual(result["time_constraint"]["mode"], "total")
        self.assertIsInstance(result["time_constraint"]["matched"], bool)

    def test_time_bounded_walk_does_not_recommend_the_starting_poi(self):
        self.places.insert(0, {
            "id": "node/at-origin", "name": "Место старта", "lat": 51.1283,
            "lon": 71.4305, "category": "mall", "category_label": "Торговый центр",
            "description": "", "opening_hours": "", "source_url": "https://www.openstreetmap.org/node/at-origin",
        })
        result = self.request(query="Хочу прогуляться 30–60 минут")
        self.assertNotIn("node/at-origin", [item["id"] for item in result["recommendations"]])

    def test_invalid_coordinates_are_rejected(self):
        with self.assertRaises(ValueError):
            self.request(lat=111)

    def test_outside_collection_area_returns_clear_coverage_message(self):
        result = self.request(lat=51.0, lon=71.47)
        self.assertEqual(result["recommendations"], [])
        self.assertIn("вне зоны", result["message"])
        self.assertIn("NQZ", result["hint"])

    def test_airport_region_requires_its_own_collected_catalog(self):
        result = self.request(lat=51.025, lon=71.465)
        self.assertEqual(result["recommendations"], [])
        self.assertIn("ещё не загружены", result["message"])


class PrivacyAndSourceTests(unittest.TestCase):
    def test_map_uses_visible_osm_tiles_and_attribution(self):
        root = Path(__file__).resolve().parents[1]
        app = (root / "app.js").read_text(encoding="utf-8")
        index = (root / "index.html").read_text(encoding="utf-8")
        self.assertIn("https://tile.openstreetmap.org/{z}/{x}/{y}.png", app)
        self.assertIn("OpenStreetMap contributors", app)
        self.assertIn("attributionControl: true", app)
        self.assertNotIn("basemaps.cartocdn.com", app)
        self.assertNotIn("arcgisonline.com", app)

    def test_official_events_calendar_is_linked_without_importing_records(self):
        root = Path(__file__).resolve().parents[1]
        index = (root / "index.html").read_text(encoding="utf-8")
        app = (root / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="officialEventsLink"', index)
        self.assertIn("visitastana.kz/", app)
        self.assertIn("about-city/where-to-go/", app)

class OsmCollectionTests(unittest.TestCase):
    def test_only_explicit_socket_and_quiet_tags_are_used(self):
        positive = derive_features("Cafe", "cafe", {"socket": "yes", "quiet": "yes"})
        negative = derive_features("Cafe", "cafe", {"socket": "no", "quiet": "no"})
        unknown = derive_features("Cafe", "cafe", {})
        self.assertTrue(positive["has_sockets"])
        self.assertTrue(positive["is_quiet"])
        self.assertFalse(negative["has_sockets"])
        self.assertFalse(negative["is_quiet"])
        self.assertIsNone(unknown["has_sockets"])
        self.assertIsNone(unknown["is_quiet"])

    def test_short_summary_uses_only_explicit_osm_tags(self):
        summary, source = short_summary("Кафе", "", {"cuisine": "italian"})
        self.assertEqual(summary, "Кафе · кухня: italian")
        self.assertEqual(source, "osm_category_tags")

    def test_source_description_is_kept_and_identified(self):
        summary, source = short_summary("Музей", "Короткое описание из OSM", {})
        self.assertEqual(summary, "Короткое описание из OSM")
        self.assertEqual(source, "osm_description")

    def test_unnamed_playground_is_retained_with_clear_name(self):
        result = normalize_element({
            "type": "way",
            "id": 321,
            "center": {"lat": 51.1, "lon": 71.4},
            "tags": {"leisure": "playground"},
        })
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Детская площадка")
        self.assertEqual(result["category"], "playground")

    def test_airport_terminal_and_group_capacity_are_source_fields(self):
        result = normalize_element({
            "type": "node",
            "id": 99,
            "lat": 51.025,
            "lon": 71.465,
            "tags": {"name": "NQZ Terminal", "aeroway": "terminal", "capacity": "120"},
        })
        self.assertEqual(result["category"], "airport_terminal")
        self.assertEqual(result["capacity"], 120)
        self.assertEqual(result["capacity_source"], "capacity")

    def test_playground_tag_is_not_hidden_by_secondary_childcare_tag(self):
        self.assertEqual(category_for({"amenity": "childcare", "leisure": "playground"})[0], "playground")

    def test_collector_queries_unnamed_playgrounds(self):
        from osm_data import build_query

        self.assertIn('nwr["leisure"="playground"]', build_query())

    def test_collector_includes_airport_terminal_and_separate_airport_area(self):
        from osm_data import COVERAGE_AREAS, build_query, point_in_coverage

        self.assertIn('"aeroway"', build_query())
        self.assertIn("nqz_airport", COVERAGE_AREAS)
        self.assertTrue(point_in_coverage(51.025, 71.465))


class StretchGoalsTests(unittest.TestCase):
    def setUp(self):
        self.places = [
            {
                "id": "node/cafe1",
                "name": "Кофейня Көктем",
                "name_kk": "Көктем кофеханасы",
                "name_en": "Koktem Coffee",
                "lat": 51.1285,
                "lon": 71.4310,
                "category": "cafe",
                "category_label": "Кафе",
                "description": "Уютная кофейня с розетками и Wi-Fi.",
                "has_sockets": True,
                "wheelchair": "yes",
                "capacity": 18,
                "capacity_source": "capacity",
                "opening_hours": "08:00-23:00",
            },
            {
                "id": "node/park1",
                "name": "Парк Нұржол",
                "name_kk": "Нұржол саябағы",
                "name_en": "Nurzhol Park",
                "lat": 51.1290,
                "lon": 71.4320,
                "category": "park",
                "category_label": "Парк",
                "description": "Центральный пешеходный бульвар.",
                "wheelchair": "yes",
                "opening_hours": "24/7",
            },
            {
                "id": "node/museum1",
                "name": "Музей Будущего Нұр Әлем",
                "name_kk": "Нұр Әлем болашақ музейі",
                "name_en": "Nur Alem Future Museum",
                "lat": 51.1300,
                "lon": 71.4330,
                "category": "museum",
                "category_label": "Музей",
                "description": "Сферический интерактивный музей.",
                "wheelchair": "yes",
                "opening_hours": "10:00-20:00",
            },
            {
                "id": "node/pub1",
                "name": "Ночной паб Harats",
                "name_kk": "Harats түнгі пабы",
                "name_en": "Harats Night Pub",
                "lat": 51.1310,
                "lon": 71.4340,
                "category": "pub",
                "category_label": "Паб",
                "description": "Живая музыка и вечерний отдых.",
                "wheelchair": "no",
                "opening_hours": "17:00-04:00",
            },
        ]
        self.dataset = {"places": self.places}
        self.dataset_patch = patch.object(server, "read_dataset", return_value=self.dataset)
        self.route_patch = patch.object(server, "route_matrix", return_value=[])
        self.provider_patch = patch.object(server, "llm_provider", return_value=server.LOCAL_GENERATOR)
        self.dataset_patch.start()
        self.route_patch.start()
        self.provider_patch.start()
        self.addCleanup(self.dataset_patch.stop)
        self.addCleanup(self.route_patch.stop)
        self.addCleanup(self.provider_patch.stop)

    def test_mini_route_generation(self):
        payload = {
            "lat": 51.1283,
            "lon": 71.4305,
            "query": "Построй мини-маршрут на 1-2 часа",
            "category": "all",
            "mode": "mini_route",
            "lang": "ru",
        }
        res = server.recommend(payload)
        self.assertTrue(res["is_mini_route"])
        self.assertIsNotNone(res["route_summary"])
        self.assertIn("segments", res["route_summary"])
        self.assertGreaterEqual(len(res["route_summary"]["segments"]), 2)
        self.assertGreater(res["route_summary"]["total_duration_minutes"], 0)

    def test_multilingual_kazakh(self):
        payload = {
            "lat": 51.1283,
            "lon": 71.4305,
            "query": "Серуендеп, кофе ішетін жақсы жер",
            "category": "all",
            "lang": "kk",
        }
        res = server.recommend(payload)
        self.assertEqual(res["lang"], "kk")
        self.assertTrue(res["recommendations"])
        first = res["recommendations"][0]
        self.assertTrue(
            "көктем" in first["name"].lower()
            or "кофе" in first["activity"].lower()
            or "жер" in first["reason"].lower()
        )

    def test_multilingual_english(self):
        payload = {
            "lat": 51.1283,
            "lon": 71.4305,
            "query": "Looking for a quiet specialty coffee shop",
            "category": "all",
            "lang": "en",
        }
        res = server.recommend(payload)
        self.assertEqual(res["lang"], "en")
        self.assertTrue(res["recommendations"])
        first = res["recommendations"][0]
        self.assertTrue(any(word in first["activity"].lower() for word in ("coffee", "stop", "minutes", "relax", "laptop")))

    def test_accessibility_hard_filter(self):
        payload = {
            "lat": 51.1283,
            "lon": 71.4305,
            "query": "Доступное место для маломобильных",
            "category": "all",
            "filter_accessibility": True,
        }
        res = server.recommend(payload)
        self.assertTrue(all(p["wheelchair"] != "no" for p in res["recommendations"]))

    def test_night_activity_intent(self):
        payload = {
            "lat": 51.1283,
            "lon": 71.4305,
            "query": "Ищу необычную ночную активность",
            "category": "all",
            "filter_night": True,
        }
        res = server.recommend(payload)
        self.assertTrue(any(p.get("category") in {"bar", "pub", "cinema", "theatre"} for p in res["recommendations"]))

    def test_group_planning_uses_explicit_capacity_and_reports_unknown(self):
        payload = {
            "lat": 51.1283,
            "lon": 71.4305,
            "query": "Ищу кафе для компании из 5 человек",
            "category": "cafe",
            "filter_group": True,
            "group_size": 5,
        }
        res = server.recommend(payload)
        self.assertEqual(len(res["recommendations"]), 1)
        self.assertEqual(res["recommendations"][0]["group_capacity"], 18)
        self.assertTrue(res["recommendations"][0]["group_capacity_verified"])
        self.assertEqual(res["group_planning"]["party_size"], 5)

    def test_local_english_reason_does_not_fall_back_to_russian_description(self):
        cafe = self.places[0]
        cafe["description"] = "Уютная кофейня рядом с парком."
        cafe["description_en"] = ""
        res = server.recommend({
            "lat": 51.1283,
            "lon": 71.4305,
            "query": "coffee",
            "category": "cafe",
            "lang": "en",
        })
        self.assertEqual(res["recommendations"][0]["category_label"], "Cafe")
        self.assertNotIn("кофейня", res["recommendations"][0]["reason"].lower())
        self.assertEqual(res["generation_mode"], server.LOCAL_GENERATOR)


class BackendEnterpriseTests(unittest.TestCase):
    def test_navigation_deep_links_present(self):
        links = server.make_navigation_links((51.1283, 71.4305), (51.1300, 71.4350))
        self.assertIn("2gis.kz", links["twogis_url"])
        self.assertIn("google.com/maps", links["google_maps_url"])
        self.assertIn("yandex.kz/maps", links["yandex_maps_url"])

    def test_health_telemetry_schema(self):
        health = server.get_health()
        self.assertEqual(health["status"], "healthy")
        self.assertIn("uptime_seconds", health)
        self.assertIn("astana_time", health)
        self.assertIn("poi_by_category", health)
        self.assertGreater(health["poi_total"], 0)

    def test_openapi_spec_structure(self):
        spec = server.get_openapi_spec()
        self.assertEqual(spec["openapi"], "3.0.3")
        self.assertIn("/api/recommend", spec["paths"])
        self.assertIn("/api/health", spec["paths"])
        self.assertIn("/api/status", spec["paths"])

    def test_rate_limiter_logic(self):
        ip = "192.0.2.100"
        self.assertTrue(server.check_rate_limit(ip))

    def test_mini_route_geojson_and_urls(self):
        dummy_items = [
            {"name": "Точка 1", "lat": 51.1283, "lon": 71.4305, "visit_minutes_min": 15, "visit_minutes_max": 30},
            {"name": "Точка 2", "lat": 51.1300, "lon": 71.4320, "visit_minutes_min": 20, "visit_minutes_max": 40},
        ]
        route = server.build_mini_route_timeline((51.1250, 71.4280), dummy_items)
        self.assertEqual(route["geojson"]["type"], "FeatureCollection")
        self.assertEqual(len(route["route_points"]), 3)
        self.assertIn("google.com/maps", route["google_maps_route_url"])
        self.assertIn("yandex.kz/maps", route["yandex_maps_route_url"])

    def test_real_route_geometry_is_marked_and_exported_in_geojson(self):
        coordinates = [[71.4280, 51.1250], [71.4310, 51.1280], [71.4350, 51.1300]]
        route = server.build_mini_route_timeline(
            (51.1250, 71.4280),
            [{"name": "Точка", "lat": 51.1300, "lon": 71.4350, "visit_minutes_min": 10, "visit_minutes_max": 20}],
            routed_coordinates=coordinates,
        )
        line = next(feature for feature in route["geojson"]["features"] if feature["geometry"]["type"] == "LineString")
        self.assertEqual(route["geometry_source"], "openrouteservice")
        self.assertEqual(line["geometry"]["coordinates"], coordinates)
        self.assertEqual(route["route_points"], [[51.1250, 71.4280], [51.1280, 71.4310], [51.1300, 71.4350]])


if __name__ == "__main__":
    unittest.main()
