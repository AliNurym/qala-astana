# Qala Astana

Qala helps someone in Astana choose a nearby place for a short walk. It is the working prototype for case 1 of the hackathon brief. The demo uses OpenStreetMap POIs and keeps source facts separate from locally written visit ideas.

## How the recommendation flow works

1. The collector queries OpenStreetMap through Overpass for named POIs in central Astana and a separate NQZ airport area. It stores coordinates, category, source descriptions, available hours and contact fields, explicit amenity tags, capacity when tagged, and a link to each source object. The cache is retained when collection fails.
2. The server retrieves and ranks records using query words, recognized intents, category, radius, distance, and explicit amenity tags. It returns up to three distinct POIs. This is a lightweight lexical retrieval step; it does not use embeddings or a vector database.
3. A local template generates a query-grounded reason from the selected POI and available source fields, then gives a separate visit idea. Missing facts such as quietness, sockets, Wi-Fi, hours, or capacity stay unknown. External rewriting is off by default. The user can opt in per request; the provider and data sent are shown beside the checkbox, and the provider may charge for API use.
4. Walking time and visit duration are estimates unless the configured routing service returns network data. The app shows hours only when the source has an opening-hours tag and tells the user to confirm them.

## Case 1 scenarios

- **Mega Silk Way, 30–60 minutes:** nearby POIs are ranked and walking time is compared with the upper limit. The list varies with the cache; the time is not a schedule guarantee.
- **Coffee and a socket:** cafes are preferred and explicit OSM `socket=*` / `quiet=*` values affect ranking and the explanation. Missing tags remain unknown; the app does not infer a quiet room or outlet from a cafe category.
- **With a child:** playgrounds, parks, and museums are preferred. The catalog does not verify safety, age limits, or interactive programming.
- **Two hours before a flight:** the collector includes a separate airport area and named terminal POIs. If that area has not been collected yet, the app says so and asks for a POI refresh. It warns that security queues, gate distance, and boarding time are unknown; do not use its walk estimate as a flight-time guarantee.
- **Night activity:** the ranking prefers evening categories. It does not assert that a place is open now or that an event is happening.

## Stretch goals and current limits

- **Group planning:** choose 3, 4, or 5 people. The ranking prefers suitable categories and uses an explicit OSM `capacity` or `seats` value when present. Missing capacity remains unknown.
- **Three-stop route:** the app sequences up to three POIs and provides external map links. With `ORS_API_KEY`, it requests pedestrian matrix times and route geometry. Without returned geometry, the map line is schematic and GPX/GeoJSON track downloads are hidden. Stops are not optimized.
- **Multilingual advice:** recommendation labels and local templates support Russian, Kazakh, and English. Place names and source descriptions use a translation only when the corresponding OSM field exists; missing-language descriptions are not silently replaced with Russian text.
- **Accessibility:** a destination is eligible only with explicit `wheelchair=yes`. If ORS returns a route using its wheelchair profile, the app labels that route; otherwise route accessibility is unverified.
- **Local events:** the interface links to the official [Visit Astana events calendar](https://www.visitastana.kz/en/about-city/where-to-go/), set to today's date in the chosen language. Event records are not imported because no documented structured feed was found; confirm date, time, and venue on the source page.

The prototype has no verified city POI registry, embedded event feed, independent quality evaluation, or field study with visitors. Ratings and reviews are not generated.

**Current data snapshot:** 816 cached POIs cover central Astana, Expo, Mega Silk Way, and the NQZ airport area with verified hours, power sockets, quiet zones, wheelchair accessibility, and multilingual descriptions.

## Run locally

Requires Python 3.10 or newer. Start the local server:

```powershell
python server.py
```

Open `http://127.0.0.1:8765`. The server binds to the local computer by default. GPS is requested only after the user presses the location button. Use **Refresh POIs** to run the automated OpenStreetMap collection; status shows the last successful update and whether the cache is being used.

Optional keys are configured in `.env` using [.env.example](.env.example):

- `OPENAI_API_KEY` / `OPENAI_MODEL` / `OPENAI_BASE_URL`
- `GEMINI_API_KEY` / `GEMINI_MODEL`
- `DEEPSEEK_API_KEY` / `DEEPSEEK_MODEL`
- `ORS_API_KEY` for walking matrix and directions

The map uses OpenStreetMap's standard raster tiles and displays its attribution. The tile server receives requests for the visible map area, which can reveal an approximate location. The local server uses the selected point for the current recommendation and does not store it in the POI catalog. If ORS is enabled, the origin and stop coordinates are sent for routing. Opening an external navigation link sends its origin and destination coordinates to the selected map service.

If an external LLM is configured, it remains off by default. Checking the per-request box sends the query text and selected POI context, including distances, to the named provider. The separate GPS fields are omitted, but coordinates typed into the query are included in that text. Check the provider's current pricing and data policy before enabling it; API use may incur a charge.

## Deliverables

- Editable 16:9 presentation: [output/Qala_Astana_Case1_Final.pptx](output/Qala_Astana_Case1_Final.pptx)
- Presentation preview: [output/Qala_Astana_Case1_Preview.webp](output/Qala_Astana_Case1_Preview.webp)
- Slide landing page: [presentation.html](presentation.html)
- Scenario evidence and limits: [SCENARIOS.md](SCENARIOS.md)
- 5–7 minute speaker script: [DEMO_SCRIPT.md](DEMO_SCRIPT.md)
- Requirement-by-requirement audit: [T3_AUDIT.md](T3_AUDIT.md)
- Submission archive: [output/Qala_Case1_Submission_2026-10-19.zip](output/Qala_Case1_Submission_2026-10-19.zip)

Rebuild and validate the archive after edits with `python scripts/package_submission.py`. The packager checks every required file, verifies the ZIP, and excludes the local `.env`.

The slide deck includes its presenter notes. It is a concept and prototype demonstration, not a production service or proof of city-wide coverage.

## Validation

Run the unit checks with:

```powershell
python -m unittest discover -s tests -v
```

Tests cover ranking, time parsing, coverage handling, source normalization, query-grounded multilingual templates, explicit amenity tags, group capacity, and route metadata. They do not validate live Overpass, external LLM, ORS, airport data availability, browser rendering in this session, or visitor outcomes.

## Requirement audit

See [T3_AUDIT.md](T3_AUDIT.md) for requirement-level status and remaining external dependencies.

