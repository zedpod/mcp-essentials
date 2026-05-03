# tripweather

> Open-Meteo geocoding + travel-day weather forecast. No country bias, no hidden city fallbacks.

Part of [mcp-essentials](../README.md). Free Open-Meteo API — no key required.

## Tools

- `geocode(query, country?, max_results, language)` → `Result[GeocodeResult]` — list candidates
- `forecast(latitude, longitude, start_date?, days, units, language)` → `Result[ForecastResult]` — by coords
- `forecast_by_query(query, country?, start_date?, days, units, language)` → `Result[ForecastResult]` — convenience; sets `meta.disambiguation_warning` on ties

`units`: `"metric"` (°C, km/h, mm) or `"imperial"` (°F, mph, in).

## Install — Open WebUI

Paste [`./owui.py`](./owui.py) into Admin → Tools.

## Install — Claude Desktop / Cursor / Cline

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
