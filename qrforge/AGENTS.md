# AGENTS.md — qrforge

> Read this before changing anything in `qrforge/`. Combine with [`../AGENTS.md`](../AGENTS.md) for repo-wide rules.

## Tool identity

- **Name**: qrforge
- **Purpose**: Generate QR codes for arbitrary text, URLs, Wi-Fi credentials, and vCard contacts. Local rendering by default; opt-in remote fallback for non-sensitive payloads.
- **Status**: stable (canonical reference for the dual-mode pattern in this repo).
- **Owner**: Orzed, LLC.

## Public surface

Both wrappers expose four functions with parallel signatures. The MCP side returns the JSON-serialized `Result`; the OWUI side returns markdown rendered by `core.render.to_markdown`.

| Function | Required args | Optional args | Returns |
|---|---|---|---|
| `qr_text` | `text` | `size, border, ec_level, use_remote_fallback, language` | `Result[QrImage]` |
| `qr_url` | `url` | `size, border, ec_level, use_remote_fallback, language` | `Result[QrImage]` |
| `qr_wifi` | `ssid` | `password, encryption, hidden, size, border, ec_level, language` | `Result[QrImage]` |
| `qr_vcard` | `full_name` | `phone, email, org, title, url, size, border, ec_level, language` | `Result[QrImage]` |

`use_remote_fallback` is **deliberately absent** from `qr_wifi` and `qr_vcard` — the security posture of those payloads forbids remote rendering. Do not add it.

## Return-shape contract

Successful response:

```json
{
  "ok": true,
  "data": {
    "format": "png",
    "source": "local" | "remote",
    "data_b64": "...",          // when source=="local"
    "remote_url": "https://...",// when source=="remote"
    "byte_length": 5821,
    "pixel_size": 256,
    "border": 4,
    "ec_level": "M",
    "payload_kind": "text" | "url" | "wifi" | "vcard",
    "payload_preview": "first 80 chars"
  },
  "meta": {
    "source": "local",
    "warning": "remote_fallback_used"   // only when remote was used
  }
}
```

Failure response:

```json
{
  "ok": false,
  "error": {
    "code": "INVALID_INPUT" | "UNSUPPORTED" | "INTERNAL",
    "message_en": "...",
    "message_tr": "...",
    "hint": "..."
  }
}
```

Both message languages are always populated (repo-wide invariant). The OWUI wrapper renders these into markdown via `core/render.py`; if you change the structured shape, regenerate goldens.

## Language / i18n

`language` defaults to `"en"`. Anything unsupported normalizes to `"en"` silently — that is, no error, just the default. Keys live in `core/i18n.py`. Adding a new error or label requires entries in **both** `en` and `tr`; the repo-level test (`tests/test_repo.py::test_i18n_key_parity`) enforces that.

When introducing a new language (say `de`):
1. Add a `"de"` block in `STRINGS` with the same keys as `"en"`.
2. Add `"de"` to `SUPPORTED`.
3. Update `tests/test_core_qr.py::TestI18n` with at least one `language="de"` assertion.

## External services

- **Local generation**: `qrcode[pil]` (optional dependency). When missing, qrforge cannot render Wi-Fi or vCard payloads (returns `UNSUPPORTED` with an install hint).
- **Remote fallback**: `https://api.qrserver.com/v1/create-qr-code/`. Only used for `qr_text` / `qr_url` when explicitly opted in. Carries no API key. Free, but has rate limits in practice.

No retry/backoff inside qrforge — there is no HTTP fetch in the happy path, only URL construction. The browser/OWUI fetches the remote PNG when rendering.

## Env vars

**None.** The optional `USE_REMOTE_FALLBACK` is configured via OWUI Valves or via the `use_remote_fallback` argument; do not introduce env-var configuration without good reason — `.env.example` does not exist for this tool intentionally.

## Test expectations

- **`tests/test_core_qr.py`** — 30+ unit tests. Pure logic. No network. Coverage target ≥ 90% on `core/`.
- **`tests/test_owui.py`** — Loads the *generated* `owui/main.py` as a synthetic module and exercises the `Tools` class. Includes a parity test against `core` to catch drift.
- **`tests/test_mcp.py`** — In-process FastMCP smoke tests. Checks tool registration, JSON-Schema, and call routing.
- **`tests/test_integration.py`** — Live tests, marked `@pytest.mark.live`. Skipped unless `RUN_LIVE=1`. qrforge has very few live paths because rendering is offline.

When changing `core/` or `owui/_wrapper.py`, run:

```bash
python tools/bundle_owui.py qrforge
pytest qrforge/tests
```

## Edge cases & known gotchas

1. **`from __future__ import annotations`** is intentionally absent from `core/qr.py` and `server.py`. Pydantic 2's generic-class machinery (`Result[T]`) needs eager annotations to resolve `Literal[...]` types in fields like `EcLevel`. If you add it, the OWUI bundle will raise `PydanticUserError: not fully defined` at import time.
2. **OWUI bundle is generated** by `tools/bundle_owui.py` from `core/` modules in the order listed in `core/__init__.py:__bundle_order__`. The order matters: `types` must come before everything that uses `Result`, `ErrorInfo`, etc. If you add a new core module, append it to `__bundle_order__` *after* its dependencies.
3. **OWUI bundle can't import sibling files.** Anything you put in `core/` is inlined; anything in `_owui_wrapper.py` is inlined. There is no third location. Tests load the generated `owui.py` via `importlib.util.spec_from_file_location` and **must** register the synthesized module in `sys.modules` before `exec_module()` so Pydantic's generic registry doesn't `KeyError`.
4. **Wi-Fi payload escaping**: `;`, `,`, `:`, `\`, and `"` must be backslash-escaped per the WIFI URI scheme. `_wifi_payload` handles this; if you touch it, run `TestQrWifi::test_special_chars_in_ssid_are_escaped`.
5. **vCard line endings are CRLF** (`\r\n`), not `\n`. Some QR scanners reject the `\n`-only form. Don't "simplify" this.
6. **EC level vs payload size**: `qrcode` raises a generic `Exception` when the payload exceeds the chosen EC level's capacity. `_build_image` translates that into `INVALID_INPUT` with a `hint.try_lower_ec`. If `qrcode`'s exception text changes upstream, the heuristic check (`"too" or "long" or "exceed"`) might miss it; widen as needed.

## How to add a method

1. Add the public function in `core/qr.py`. Sketch:
   ```python
   def qr_<thing>(arg: str, *, size=512, border=4, ec_level="M", language="en") -> Result[QrImage]: ...
   ```
2. Add new `i18n.py` keys for any new error/label strings (en + tr).
3. Add unit tests in `tests/test_core_qr.py`.
4. Re-export the function from `core/__init__.py`.
5. Add a thin OWUI wrapper method in `_owui_wrapper.py`.
6. Add a `@mcp.tool()` wrapper in `server.py` returning `result.model_dump(mode="json")`.
7. Run `python tools/bundle_owui.py qrforge` to regenerate `owui.py`.
8. `make test && make check-bundle` must be green.

## TODOs / known limitations

- **vCard 4.0**: only 3.0 is supported; 4.0 has a different field set (e.g. `KIND`, structured names). Out of scope for v1.
- **Custom colors / logo overlay**: not supported. Would need additional `qrcode` configuration plus a logo composite step (Pillow). Add as a flag with sensible defaults if needed.
- **Batch generation**: callers issue one tool call per QR. If you need throughput, build it as a separate `qr_batch(items)` MCP tool that fans out to `_build_image` directly (no parallelism is needed since generation is fast).
