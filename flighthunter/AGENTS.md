# AGENTS.md — flighthunter

> Read with [`../AGENTS.md`](../AGENTS.md).

## Public surface
- `search_flights(origin, destination, departure_date, return_date?, cabin_class, adults, children, infants, currency, *, language, api_key=None)` → `Result[FlightSearch]`

## Architecture
- `core/search.py` — single SerpAPI call (`engine=google_flights`); parses `best_flights` + `other_flights`; surfaces `price_insights` and the deep-link to Google Flights.
- IATA validation, passenger-count validation, date validation **before** any HTTP.
- API key resolution order: explicit `api_key=` argument → `FLIGHTHUNTER_SERPAPI_KEY` env → `SERPAPI_API_KEY` env. Missing key → typed `MISSING_API_KEY` error.

## Edge cases
- **Multi-city** is not exposed in v1 — only `one_way` and `round_trip`. Add a separate function if needed.
- **`travel_class` mapping**: SerpAPI uses 1/2/3/4 codes; we map at the call site.
- **`gl` parameter**: forced to `"us"` when language is `"en"`; otherwise mirrors the language code.
- **`hl`** (UI language) mirrors the `language` parameter.
- **No retry on 4xx** other than 408/429/5xx; SerpAPI 4xx usually means a permanent input/auth problem.

## Cost discipline
SerpAPI charges per search. Live tests are gated by `RUN_LIVE=1` and run **one** real query — do not loop or fan out in tests. Keep the unit suite respx-mocked.

## i18n
`STRINGS["en"]` and `STRINGS["tr"]` parity is enforced by the repo-level test.

## Tests
- `tests/test_core.py` — validation + happy/error paths (respx).
- `tests/test_owui.py`, `tests/test_server.py` — bundle/MCP smoke.
- `tests/test_integration.py` — single live query, gated.

## How to add a feature (e.g. multi-city)
1. Extend `core/types.py` (`TripType` already includes `multi_city`).
2. Add input validation + SerpAPI param mapping in `core/search.py`.
3. Add tests using respx fixtures.
4. Add a new MCP tool (or extend signature) in `server.py`; mirror in `_owui_wrapper.py`.
5. `python tools/bundle_owui.py flighthunter && pytest flighthunter/tests`.
