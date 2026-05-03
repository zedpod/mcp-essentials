# tripweather

> Open-Meteo geocoding + travel-day weather forecast. No country bias, no hidden city fallbacks.

Part of [mcp-essentials](../README.md). Free Open-Meteo API - no key required.

## Tools

- `geocode(query, country?, max_results, language)` → `Result[GeocodeResult]` - list candidates
- `forecast(latitude, longitude, start_date?, days, units, language)` → `Result[ForecastResult]` - by coords
- `forecast_by_query(query, country?, start_date?, days, units, language)` → `Result[ForecastResult]` - convenience; sets `meta.disambiguation_warning` on ties

`units`: `"metric"` (°C, km/h, mm) or `"imperial"` (°F, mph, in).

## Install - Open WebUI

1. Paste [`./owui.py`](./owui.py) into Admin → Tools.
2. Description field (optional - docstrings already carry bilingual EN/TR triggers):
   ```text
   Open-Meteo geocoding plus daily weather forecast (1 to 16 days). No API key required.

   Use when the user asks for:
   - the weather for a place
   - a forecast for a city or coordinates over several days
   - geocoding a place name to lat/lon (disambiguation)

   Do NOT use for: climate trends, historical weather analysis, past-date weather, or generic "is it raining" questions without a place.
   ```
3. Configure Valves (`DEFAULT_LANGUAGE`, `DEFAULT_UNITS`, `DEFAULT_DAYS`).

## Install - Claude Desktop / Cursor / Cline

```json
{
  "mcpServers": {
    "tripweather": {
      "command": "python",
      "args": ["-m", "tripweather"],
      "cwd": "/absolute/path/to/mcp-essentials",
      "env": { "PYTHONPATH": "/absolute/path/to/mcp-essentials" }
    }
  }
}
```

## License

Apache 2.0. Forecast data: Open-Meteo (CC-BY 4.0).

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
