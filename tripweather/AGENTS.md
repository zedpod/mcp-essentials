# AGENTS.md - tripweather

> Read with [`../AGENTS.md`](../AGENTS.md). Total-rewrite tool - the legacy `weather_brief` god-tool was retired.

## Public surface
- `geocode(query, country=None, max_results=5, *, language)` → `Result[GeocodeResult]`
- `forecast(latitude, longitude, *, start_date=None, days=3, units="metric", language)` → `Result[ForecastResult]`
- `forecast_by_query(query, country=None, *, start_date=None, days=3, units, language)` → `Result[ForecastResult]`

## Architecture
- `core/geocode.py` - Open-Meteo geocoding. **No country bias**, **no hardcoded city fallback** (the legacy `_known_place_fallback` is gone).
- `core/forecast.py` - Open-Meteo `/v1/forecast`. Daily fields only. Honors `units`.
- `core/wmo.py` - WMO weather codes mapped to en/tr labels.
- `core/render.py` - markdown.

## Edge cases
- **Invalid coords** rejected with explicit message in en + tr.
- **Disambiguation**: when the second candidate's `ranking_score` is within 1.0 of the top one, `meta.disambiguation_warning=True`. The LLM can then ask the caller to clarify or pass lat/lon.
- **`units="imperial"`** maps to fahrenheit/mph/inch via Open-Meteo params. We don't post-convert.
- **`start_date`** is optional; without it, we use Open-Meteo's `forecast_days=N`.
- **Past dates**: not supported in v1 (Open-Meteo's forecast endpoint covers only forward window).

## Killed legacy behavior
- `_known_place_fallback` (Uzunköprü, Edirne, Istanbul) - gone.
- Country-score bias toward TR - gone.
- `trip_purpose` and `sensitivity` substring matching - gone (callers compose advice from raw forecasts).
- Default `language="tr"` - replaced with `language="en"`.

## Tests
- `tests/test_core.py` - geocode + forecast happy/error + disambiguation.
- `tests/test_owui.py` / `tests/test_server.py` - bundle/MCP smoke.
- `tests/test_integration.py` - `RUN_LIVE=1`.
