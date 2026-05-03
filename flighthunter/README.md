# flighthunter

> Flight search via [SerpAPI](https://serpapi.com)'s Google Flights engine.

Part of [mcp-essentials](../README.md). **Requires a SerpAPI key.**

## Tool

`search_flights(origin, destination, departure_date, return_date?, cabin_class, adults, children, infants, currency, language)` → `Result[FlightSearch]`

`origin` and `destination` must be 3-letter IATA airport codes (e.g. `IST`, `LHR`, `JFK`). `departure_date` and `return_date` use `YYYY-MM-DD`. The `data.search_url` field contains a Google Flights deep link for booking.

## Setup - API key

1. Create a free [SerpAPI account](https://serpapi.com/users/sign_up) (100 searches/month on the free tier).
2. Copy your API key.
3. Set it via env var (preferred) or via the OWUI Valve:

```bash
# Local dev
echo 'FLIGHTHUNTER_SERPAPI_KEY=your-key-here' > flighthunter/.env

# In claude_desktop_config.json
"flighthunter": {
  "command": "python",
  "args": ["-m", "flighthunter"],
  "cwd": "/absolute/path/to/mcp-essentials",
  "env": {
    "PYTHONPATH": "/absolute/path/to/mcp-essentials",
    "FLIGHTHUNTER_SERPAPI_KEY": "your-key-here"
  }
}
```

## Install - Open WebUI

1. Paste [`./owui.py`](./owui.py) into Admin → Tools.
2. Description field (optional - docstrings already carry bilingual EN/TR triggers):
   ```text
   Search flights via SerpAPI Google Flights. Returns ranked options with prices and a Google Flights deep-link.

   Use when the user provides origin and destination IATA codes (or asks you to fetch them) plus a date and asks to:
   - find flights between two airports
   - compare ticket prices for a route
   - search a round-trip with specific dates

   Do NOT use for: trains, buses, ferries, hotels, car rentals, or generic travel advice without dates and airports. Each call costs 1 SerpAPI credit.
   ```
3. Either set the `SERPAPI_API_KEY` Valve or supply `FLIGHTHUNTER_SERPAPI_KEY` in the runtime env.

## Errors

| Code | When |
|---|---|
| `MISSING_API_KEY` | No SerpAPI key configured |
| `INVALID_INPUT` | Bad IATA code, malformed date, return < departure, invalid cabin/passenger combination |
| `RATE_LIMITED` | SerpAPI 429 (out of credits or throttled) |
| `UPSTREAM_ERROR` | SerpAPI returned an `error` field or non-2xx status |

## License

Apache 2.0.

---

*Part of mcp-essentials by [Orzed](https://orzed.com).*
