install:
	uv sync --all-groups --all-extras

tests: install
	uv run ruff check .
	uv run ruff format --check .
	uv run pytest

audit: install
	uv run pip-audit

build: install
	uv build
