"""Build the overlay HTML/JS shared between OWUI mode and the MCP localhost server.

The JS is a single self-contained IIFE that:
- Renders a modal overlay with the prompt, options, and (optionally) a custom
  free-text input.
- Implements keyboard navigation, focus trap, prefers-reduced-motion handling,
  and a search filter that auto-shows when there are >10 options.
- Posts the answer back through one of two transports:
    - OWUI mode: resolves a Promise; the OWUI `__event_call__` channel reads it.
    - MCP mode: POSTs JSON to the embedded `/answer` endpoint with a CSRF token.

The two modes differ only by the bootstrap snippet at the bottom.
"""

import json
from typing import Literal

from .i18n import t
from .types import Question

Mode = Literal["owui", "localhost"]


_BASE_CSS = """
* { box-sizing: border-box; }
:host, html, body { margin: 0; padding: 0; }
.au-backdrop {
  position: fixed; inset: 0; z-index: 99999;
  background: rgba(15, 17, 22, 0.78);
  display: flex; align-items: center; justify-content: center;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #e5e9f0;
  animation: au-fade 0.18s ease-out;
}
@media (prefers-reduced-motion: reduce) {
  .au-backdrop, .au-card, .au-option { animation: none !important; transition: none !important; }
}
@keyframes au-fade { from { opacity: 0; } to { opacity: 1; } }
.au-card {
  background: #1e1e2e; border-radius: 14px; padding: 20px 22px 18px;
  width: min(560px, calc(100vw - 24px));
  max-height: 90vh; display: flex; flex-direction: column;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.55);
  border: 1px solid rgba(205, 214, 244, 0.08);
  animation: au-pop 0.22s cubic-bezier(0.21, 1.02, 0.73, 1) both;
}
@keyframes au-pop { from { transform: translateY(8px) scale(0.98); opacity: 0; } to { transform: none; opacity: 1; } }
.au-prompt { font-size: 16px; line-height: 1.45; margin: 0 0 12px; font-weight: 500; }
.au-search {
  width: 100%; padding: 8px 10px; border-radius: 8px; border: 1px solid #45475a;
  background: #181825; color: inherit; font-size: 14px; margin: 0 0 10px;
}
.au-search::placeholder { color: #a6adc8; opacity: 0.85; }
.au-options { overflow-y: auto; max-height: 50vh; padding-right: 4px; margin: 0; padding-left: 0; list-style: none; }
.au-option {
  padding: 10px 12px; border-radius: 10px; cursor: pointer; min-height: 44px;
  display: flex; flex-direction: column; gap: 2px;
  background: #181825; margin-bottom: 6px;
  border: 1px solid transparent;
  transition: background-color 0.12s;
}
.au-option:hover, .au-option.au-focus { background: #313244; }
.au-option.au-selected { border-color: var(--au-accent); background: rgba(232, 113, 58, 0.12); }
.au-option-label { font-size: 14px; }
.au-option-desc { font-size: 12px; color: #a6adc8; }
.au-option-key { float: right; font-size: 11px; color: #a6adc8; opacity: 0.8; }
.au-custom { margin-top: 12px; }
.au-custom textarea {
  width: 100%; min-height: 64px; resize: vertical; padding: 8px 10px;
  border-radius: 8px; border: 1px solid #45475a; background: #181825; color: inherit;
  font-family: inherit; font-size: 14px;
}
.au-actions { display: flex; gap: 8px; justify-content: space-between; align-items: center; margin-top: 12px; }
.au-meta { font-size: 12px; color: #a6adc8; }
.au-btn {
  border: 0; padding: 9px 14px; border-radius: 8px; cursor: pointer;
  font-size: 14px; min-height: 36px; font-weight: 500;
}
.au-btn-primary { background: var(--au-accent); color: #1e1e2e; }
.au-btn-primary[disabled] { opacity: 0.4; cursor: not-allowed; }
.au-btn-ghost { background: transparent; color: #cdd6f4; }
.au-btn-ghost:hover { background: #313244; }
.au-warning { background: #f9e2af; color: #1e1e2e; padding: 6px 8px; border-radius: 8px; font-size: 12px; margin-bottom: 8px; }
@media (max-width: 640px) {
  .au-backdrop { align-items: flex-end; }
  .au-card { width: 100vw; max-height: 92vh; border-radius: 14px 14px 0 0; }
}
"""


def _js_payload(question: Question, lang: str, mode: Mode, csrf_token: str = "") -> str:
    options_payload = [
        {"label": o.label, "description": o.description, "value": o.value or o.label}
        for o in question.options
    ]
    config = {
        "prompt": question.prompt,
        "options": options_payload,
        "mode": question.mode,
        "allow_custom": question.allow_custom,
        "required": question.required,
        "min_select": question.min_select,
        "max_select": question.max_select,
        "timeout_s": question.timeout_s,
        "labels": {
            "skip": t("label.skip", lang),
            "cancel": t("label.cancel", lang),
            "confirm": t("label.confirm", lang),
            "search": t("label.search", lang),
            "custom_input": t("label.custom_input", lang),
        },
        "accent": question.accent,
        "csrf_token": csrf_token if mode == "localhost" else "",
    }
    return json.dumps(config, ensure_ascii=False)


_OVERLAY_JS_BODY = r"""
return (function() {
  return new Promise(function(resolve) {
    var CFG = __CONFIG__;
    var TRANSPORT = '__TRANSPORT__';

    var existing = document.getElementById('orzed-askuser-root');
    if (existing) existing.remove();

    var root = document.createElement('div');
    root.id = 'orzed-askuser-root';
    root.className = 'au-backdrop';
    root.style.setProperty('--au-accent', CFG.accent || '#E8713A');
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');

    var card = document.createElement('div');
    card.className = 'au-card';
    root.appendChild(card);

    var promptEl = document.createElement('h2');
    promptEl.className = 'au-prompt';
    promptEl.id = 'au-prompt-id';
    promptEl.textContent = CFG.prompt;
    card.setAttribute('aria-labelledby', 'au-prompt-id');
    card.appendChild(promptEl);

    var elapsedStart = Date.now();
    var selected = new Set();
    var focusIdx = 0;
    var customInput = null;

    var optionsList = document.createElement('ul');
    optionsList.className = 'au-options';
    optionsList.setAttribute('role', CFG.mode === 'multi' ? 'listbox' : 'radiogroup');
    optionsList.setAttribute('aria-multiselectable', CFG.mode === 'multi' ? 'true' : 'false');
    card.appendChild(optionsList);

    var search = null;
    if (CFG.options && CFG.options.length > 10) {
      search = document.createElement('input');
      search.type = 'search';
      search.className = 'au-search';
      search.placeholder = CFG.labels.search;
      search.setAttribute('aria-label', CFG.labels.search);
      card.insertBefore(search, optionsList);
      search.addEventListener('input', renderOptions);
    }

    function visibleOptions() {
      var q = (search && search.value || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
      if (!q) return CFG.options.map(function(o, i) { return { o: o, i: i }; });
      return CFG.options.map(function(o, i) { return { o: o, i: i }; }).filter(function(p) {
        var hay = (p.o.label + ' ' + (p.o.description || '')).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
        return hay.indexOf(q) !== -1;
      });
    }

    function renderOptions() {
      optionsList.innerHTML = '';
      var visible = visibleOptions();
      visible.forEach(function(pair, vIdx) {
        var li = document.createElement('li');
        li.className = 'au-option';
        li.tabIndex = -1;
        li.setAttribute('role', CFG.mode === 'multi' ? 'option' : 'radio');
        if (selected.has(pair.i)) {
          li.classList.add('au-selected');
          li.setAttribute('aria-selected', 'true');
        }
        if (vIdx === focusIdx) li.classList.add('au-focus');

        var lblEl = document.createElement('div');
        lblEl.className = 'au-option-label';
        lblEl.textContent = pair.o.label;
        if (vIdx < 9) {
          var key = document.createElement('span');
          key.className = 'au-option-key';
          key.textContent = String(vIdx + 1);
          lblEl.appendChild(key);
        }
        li.appendChild(lblEl);

        if (pair.o.description) {
          var desc = document.createElement('div');
          desc.className = 'au-option-desc';
          desc.textContent = pair.o.description;
          li.appendChild(desc);
        }
        li.addEventListener('click', function() { onPick(pair.i); });
        optionsList.appendChild(li);
      });
      updateConfirmEnabled();
    }

    var actions = document.createElement('div');
    actions.className = 'au-actions';
    var meta = document.createElement('span');
    meta.className = 'au-meta';
    actions.appendChild(meta);

    var btnGroup = document.createElement('div');
    btnGroup.style.display = 'flex';
    btnGroup.style.gap = '8px';

    var btnSkip = null;
    if (!CFG.required) {
      btnSkip = document.createElement('button');
      btnSkip.className = 'au-btn au-btn-ghost';
      btnSkip.textContent = CFG.labels.skip;
      btnSkip.addEventListener('click', function() { finish('skip'); });
      btnGroup.appendChild(btnSkip);
    }
    var btnCancel = document.createElement('button');
    btnCancel.className = 'au-btn au-btn-ghost';
    btnCancel.textContent = CFG.labels.cancel;
    btnCancel.addEventListener('click', function() { finish('cancelled'); });
    btnGroup.appendChild(btnCancel);

    var btnConfirm = document.createElement('button');
    btnConfirm.className = 'au-btn au-btn-primary';
    btnConfirm.textContent = CFG.labels.confirm;
    btnConfirm.addEventListener('click', function() { confirmSelection(); });
    btnGroup.appendChild(btnConfirm);

    actions.appendChild(btnGroup);
    card.appendChild(actions);

    if (CFG.mode === 'free_text' || CFG.allow_custom) {
      customInput = document.createElement('div');
      customInput.className = 'au-custom';
      var ta = document.createElement('textarea');
      ta.placeholder = CFG.labels.custom_input;
      ta.setAttribute('aria-label', CFG.labels.custom_input);
      customInput.appendChild(ta);
      customInput._ta = ta;
      card.insertBefore(customInput, actions);
    }

    function onPick(idx) {
      if (CFG.mode === 'single') {
        selected.clear(); selected.add(idx); confirmSelection();
        return;
      }
      if (CFG.mode === 'multi') {
        if (selected.has(idx)) selected.delete(idx); else selected.add(idx);
        renderOptions();
      }
    }

    function updateConfirmEnabled() {
      if (CFG.mode === 'free_text') {
        btnConfirm.disabled = false;
        return;
      }
      var ok = true;
      if (CFG.mode === 'multi') {
        var n = selected.size;
        if (CFG.min_select && n < CFG.min_select) ok = false;
        if (CFG.max_select && n > CFG.max_select) ok = false;
        if (n === 0 && !(customInput && customInput._ta && customInput._ta.value.trim())) ok = false;
        meta.textContent = n + (CFG.min_select ? ' / ≥' + CFG.min_select : '') +
          (CFG.max_select ? ' (max ' + CFG.max_select + ')' : '');
      } else {
        ok = selected.size > 0 || !!(customInput && customInput._ta && customInput._ta.value.trim());
      }
      btnConfirm.disabled = !ok;
    }

    function confirmSelection() {
      var customText = customInput && customInput._ta ? customInput._ta.value.trim() : '';
      if (CFG.mode === 'free_text' || (selected.size === 0 && customText)) {
        if (!customText) { return; }
        finish('custom', { custom_text: customText });
        return;
      }
      var indices = Array.from(selected).sort(function(a, b) { return a - b; });
      var values = indices.map(function(i) { return CFG.options[i].value; });
      finish('select', { indices: indices, values: values });
    }

    function finish(type, extra) {
      extra = extra || {};
      var elapsed_ms = Date.now() - elapsedStart;
      var answer = Object.assign({ type: type, indices: [], values: [], custom_text: null, elapsed_ms: elapsed_ms }, extra);
      cleanup();
      if (TRANSPORT === 'localhost') {
        fetch('/answer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Token': CFG.csrf_token },
          body: JSON.stringify(answer),
        }).finally(function() {
          document.body.innerHTML = '<p style="font-family: sans-serif; padding: 24px; color: #cdd6f4; background: #1e1e2e; min-height: 100vh; margin: 0;">You can close this tab.</p>';
        });
      }
      resolve(answer);
    }

    function cleanup() {
      document.removeEventListener('keydown', onKey);
      if (timer) clearTimeout(timer);
      try { root.remove(); } catch (e) {}
    }

    function onKey(e) {
      if (e.key === 'Escape') {
        e.preventDefault();
        if (CFG.required) {
          card.animate([{ transform: 'translateX(-4px)' }, { transform: 'translateX(4px)' }, { transform: 'none' }], { duration: 180 });
        } else { finish('skip'); }
        return;
      }
      if (e.key === 'Enter' && (e.target.tagName !== 'TEXTAREA')) {
        e.preventDefault(); confirmSelection(); return;
      }
      if (e.key >= '1' && e.key <= '9') {
        var n = parseInt(e.key, 10) - 1;
        var visible = visibleOptions();
        if (n < visible.length) { e.preventDefault(); onPick(visible[n].i); }
        return;
      }
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        var visible = visibleOptions();
        if (!visible.length) return;
        focusIdx = (focusIdx + (e.key === 'ArrowDown' ? 1 : -1) + visible.length) % visible.length;
        renderOptions();
        // Tab to keep focus within the modal.
      }
      if (e.key === 'Tab') {
        // simple focus trap between buttons + textarea + search
        var focusables = Array.prototype.slice.call(card.querySelectorAll('button, textarea, input'));
        var first = focusables[0]; var last = focusables[focusables.length - 1];
        if (!first) return;
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    }

    document.addEventListener('keydown', onKey);
    document.body.appendChild(root);
    renderOptions();
    if (customInput && customInput._ta) {
      customInput._ta.addEventListener('input', updateConfirmEnabled);
    }

    var timer = setTimeout(function() { finish('timeout'); }, Math.max(1, CFG.timeout_s) * 1000);
    setTimeout(function() {
      if (search) search.focus();
      else btnConfirm.focus();
    }, 50);
  });
})();
"""


_LOCALHOST_BOOTSTRAP = "// localhost mode - promise return is unused; transport is the fetch above."


def build_overlay_js(question: Question, *, language: str = "en", mode: Mode = "owui",
                      csrf_token: str = "") -> str:
    """Build the IIFE returning a Promise<Answer>. For OWUI mode."""
    config = _js_payload(question, language, mode, csrf_token)
    js = _OVERLAY_JS_BODY.replace("__CONFIG__", config).replace("__TRANSPORT__", mode)
    return js


def build_localhost_html(question: Question, *, language: str = "en", csrf_token: str) -> str:
    """Wrap the overlay JS in a standalone HTML page for the MCP localhost server."""
    js = build_overlay_js(question, language=language, mode="localhost", csrf_token=csrf_token)
    title = t("title", language)
    # The IIFE returns a Promise we ignore in localhost mode (transport is fetch).
    # We still execute it for the side-effect of rendering the overlay.
    return f"""<!doctype html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>{_BASE_CSS}</style>
</head>
<body>
  <script>
  (function() {{
    {js}
  }})();
  </script>
</body>
</html>"""


def build_owui_overlay_call(question: Question, *, language: str = "en") -> str:
    """OWUI hosts inject CSS via a separate channel, but our JS injects its own
    `<style>` element so we don't depend on that. This wraps the IIFE for OWUI's
    `__event_call__({"type":"execute","data":{"code":"..."}})` runtime.
    """
    js = build_overlay_js(question, language=language, mode="owui")
    style_inject = (
        "var s=document.createElement('style');"
        f"s.textContent={json.dumps(_BASE_CSS)};"
        "document.head.appendChild(s);"
    )
    return f"{style_inject}\n{js}"
