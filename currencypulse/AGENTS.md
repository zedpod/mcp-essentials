# AGENTS.md — currencypulse

> Read this plus [`../AGENTS.md`](../AGENTS.md) before changing currencypulse.

## Tool identity

Multi-source FX. Stable. Owned by Orzed, LLC.

## Public surface

| Function | Returns |
|---|---|
| `rate(base, quote, on?, *, language)` | `Result[Rate]` |
| `convert(amount, base, quote, on?, *, language)` | `Result[Conversion]` |
| `snapshot(base, symbols?, *, language)` | `Result[Snapshot]` |
| `timeseries(base, quote, start, end, *, language)` | `Result[TimeSeries]` |

All accept ISO 4217 codes. Crypto codes are explicitly rejected with `UNSUPPORTED`.

## Provider chain

Defined in [`core/providers.py`](./core/providers.py). Iterate in order; first that returns data wins. The chosen provider lands in `Rate.source` and `meta.source` so callers can attribute.

- **Frankfurter** — ECB-backed, free, covers TRY
- **exchangerate.host** — broad ISO 4217 coverage
- **OpenExchangeRates** — only when `CURRENCYPULSE_OXR_APP_ID` env set; OXR free tier is USD-anchored, we cross-rate via USD
- **TCMB** — Turkish central bank, TRY-only pairs (or TRY-cross). Used as the last resort because XML parsing is more fragile.

When adding a provider:
1. Implement `supports(base, quote, on_date) / rate / snapshot / timeseries` to match the duck type used by `_try_providers`.
2. Append it to `build_providers()` in the right priority slot.
3. Add tests under `tests/test_core_fx.py` mocking its endpoint with `respx`.

## Caching

In-memory dict in `core.fx._cache`, 5-minute TTL keyed by `(method, base, quote, date)`. Cleared per-test via the autouse fixture in `conftest.py`. Not shared across processes — that's intentional.

## Locale-neutral formatting

`core/render.py:_fmt_number` chooses thousands/decimal separators by language. The structured payload always carries raw `float`s — formatting is a render concern, never a data concern.

## Edge cases

- **Same currency** (e.g. `rate("USD", "USD")`) short-circuits before any HTTP call. Returns 1.0 with `source="identity"`.
- **Deprecated codes** (`HRK`, `MRO`, `STD`, etc.) are mapped to their successors at validation time; the original code shows up in `meta.deprecated`.
- **`on` date** in the future — providers return their latest available; no retroactive validation.
- **Range > 366 days** rejected with `INVALID_INPUT` — keeps `timeseries` predictable in cost.
- **OXR free tier is USD-anchored** — we always pull rates with `symbols={base, quote}` and cross-rate manually.
- **TCMB XML schema** is sensitive; failures fall through to the next provider rather than surfacing a parse error.

## i18n

All user-visible strings in `core/i18n.py`. Adding a key requires both `en` and `tr`; `tests/test_repo.py::test_i18n_key_parity` enforces it.

## Env vars

| Var | Effect |
|---|---|
| `CURRENCYPULSE_OXR_APP_ID` | Enables OXR fallback |

`.env.example` documents this. No `load_dotenv()` in production code.

## Tests

- `tests/test_core_fx.py` — happy path + error path + provider chain fall-through (respx-mocked)
- `tests/test_owui.py` — bundle parity smoke
- `tests/test_server.py` — in-process FastMCP smoke
- `tests/test_integration.py` — live, gated by `RUN_LIVE=1`

`conftest.py` autouse-clears the in-memory cache between tests so they don't leak.

## How to add a method

1. New function in `core/fx.py` (consume `core.providers` chain).
2. New `i18n.py` keys (en + tr).
3. Add to `core/__init__.py` re-exports.
4. Add a thin `@mcp.tool()` wrapper in `server.py` returning `.model_dump(mode="json")`.
5. Add OWUI-side method in `_owui_wrapper.py`, calling `to_markdown(...)`.
6. `python tools/bundle_owui.py currencypulse`.
7. Add tests + run `pytest`.
