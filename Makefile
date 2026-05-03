TOOLS := askuser currencypulse flighthunter pagesignal paperforge qrforge signalbrief sitepulse tripweather tubescript

.PHONY: help install-dev install-tools test test-live lint fmt bundle check-bundle clean

help:
	@echo "make install-dev      Install dev tooling (pytest, ruff, respx, mcp)"
	@echo "make install-tools    Install runtime deps for all tools"
	@echo "make test             Run mocked unit + integration tests"
	@echo "make test-live        Run live-API tests (RUN_LIVE=1)"
	@echo "make lint             ruff check"
	@echo "make fmt              ruff format + auto-fix"
	@echo "make bundle           Generate <tool>/owui/main.py from each tool's core/"
	@echo "make check-bundle     Verify OWUI bundles are up-to-date with core (CI)"
	@echo "make clean            Remove caches"

install-dev:
	pip install -r requirements-dev.txt

install-tools:
	@for t in $(TOOLS); do \
		if [ -f $$t/requirements.txt ]; then \
			echo "=== $$t ==="; \
			pip install -r $$t/requirements.txt; \
		fi \
	done

test:
	pytest

test-live:
	RUN_LIVE=1 pytest -m live

lint:
	ruff check .

fmt:
	ruff format .
	ruff check --fix .

bundle:
	@for t in $(TOOLS); do \
		if [ -d $$t/core ]; then \
			echo "=== bundling $$t ==="; \
			python tools/bundle_owui.py $$t; \
		fi \
	done

check-bundle:
	@for t in $(TOOLS); do \
		if [ -d $$t/core ]; then \
			python tools/bundle_owui.py $$t --check || exit 1; \
		fi \
	done

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
