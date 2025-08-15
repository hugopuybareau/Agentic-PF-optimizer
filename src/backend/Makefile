.DEFAULT_GOAL := all

.PHONY: lint
lint:
	uv run ruff check silveragents/ tests/
	uv run ruff format --check silveragents/ tests/

.PHONY: format
format:
	uv run ruff check --fix silveragents/ tests/
	uv run ruff format silveragents/ tests/

.PHONY: ty
ty:
	uv run ty check silveragents

typecheck: ty

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
