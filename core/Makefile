# .DEFAULT_GOAL := help

.PHONY: fix
fix:  ## Fix code formatting, linting and sorting imports
	python3 -m black .
	python3 -m ruff --fix .
	python3 -m mypy --no-site-packages .

.PHONY: pip
pip: pip_update  ## Compile requirements
	python3 -m piptools compile --generate-hashes --no-header --quiet --resolver=backtracking --upgrade --output-file requirements/test.txt requirements/test.in

.PHONY: pip_update
pip_update:  ## Update requirements and dependencies
	python3 -m pip install --quiet --upgrade pip~=23.0.0 pip-tools~=6.12.0 setuptools~=67.4.0 wheel~=0.38.0

.PHONY: precommit
precommit:  ## Fix code formatting, linting and sorting imports
	python3 -m pre_commit run --all-files

.PHONY: precommit_update
precommit_update:  ## Update pre_commit
	python3 -m pre_commit autoupdate

.PHONY: pytest
pytest:  ## Run debugging test
	python3 -m pytest --capture=no --durations 10

.PHONY: report
report:  ## Run coverage report
	./scripts/report.sh

.PHONY: test
test:  ## Run test
	PYTHONPATH=src/ python -m pytest --cache-clear

.PHONY: help
help:
	@echo "[Help] Makefile list commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
