.PHONY: lint typecheck test cov parity hydro independent seismic legal \
        e2e load a11y lighthouse security sbom data-tdth clean gate-all \
        check-auth publish citation data-gfd data-jrc

data-jrc:
	uv run python -m app.data_pipeline.jrc_flood

data-gfd:
	uv run python -m app.data_pipeline.gee_flood

data-tdth:
	uv run python -m app.data_pipeline.load_tdth

check-auth:
	uv run python -m app.data_pipeline.check_auth

citation:
	uv run python -m app.data_pipeline.publish --citation

publish:
	uv run python -m app.data_pipeline.publish

lint:
	uv run ruff check .

typecheck:
	uv run mypy --strict app

test:
	uv run pytest -q

cov:
	uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=90

parity:
	uv run pytest -q tests/test_parity.py

hydro:
	uv run pytest -q tests/test_hydro.py

independent:
	uv run pytest -q tests/test_independent_validation.py

seismic:
	uv run pytest -q tests/test_seismic_crosscheck.py

legal:
	uv run pytest -q tests/test_veto_legal.py

e2e:
	node node_modules/playwright/cli.js test --config tests/e2e/playwright.config.js

load:
	YRKDS_RATE_LIMIT=200000 docker compose up -d --force-recreate api
	sleep 8
	k6 run tests/load.js
	docker compose up -d --force-recreate api

a11y:
	node node_modules/playwright/cli.js test --config tests/e2e/playwright.config.js --grep "WCAG"

lighthouse:
	bash scripts/lighthouse.sh

security:
	uv pip freeze | grep -viE '^(-e |skor.motoru|yrkds)' > /tmp/yrkds_req.txt
	uv run pip-audit --strict -r /tmp/yrkds_req.txt
	cd skor_motoru && cargo audit --deny warnings

sbom:
	uv run cyclonedx-py environment -o docs/sbom.json

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov

# tek komut; kirmizi kapi varsa make basarisiz doner
gate-all: lint typecheck test cov parity hydro independent seismic legal e2e a11y lighthouse load security sbom
	@echo "TUM KAPILAR YEŞİL"
