.DEFAULT_GOAL := all

.PHONY: install
install:
	@which uv > /dev/null 2>&1 || (echo "Installing uv..." && curl -LsSf https://astral.sh/uv/0.6.5/install.sh | sh)
	uv sync --all-extras --all-packages
	uv run pre-commit install -t pre-push
	(cd src/frontend && npm install)

.PHONY: format
format:
	@make -C src/backend format

.PHONY: lint-py
lint-py:
	@make -C src/backend lint

.PHONY: lint
lint:
	@make lint-py

.PHONY: mypy
mypy:
	@make -C src/backend mypy

.PHONY: typecheck
typecheck:
	@make mypy

.PHONY: test
test:
	uv run pytest tests

.PHONY: all
all: lint typecheck test

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '.*DS_Store'`
	rm -rf .cache
	rm -rf .*_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -rf .eggs
	rm -rf .ropeproject
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf public
	rm -rf .hypothesis
	rm -rf .profiling
	rm -rf .benchmarks
