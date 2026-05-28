PACKAGE_SLUG=celerpy
PYTHON:=poetry run python
PYTHON_ENV:=poetry run

.PHONY: all
all: poetry.lock

.PHONY: install
install:
	poetry install

poetry.lock: pyproject.toml
	poetry lock

.PHONY: pre-commit
pre-commit: poetry.lock
	$(PYTHON_ENV) pre-commit install

#
# Formatting
#
.PHONY: style
style: style/format style/check style/dapperdata style/tomlsort

# NOTE: formatting must occur before style check
.PHONY: style/format
style/format:
	$(PYTHON) -m ruff format .

.PHONY: style/check
style/check:
	$(PYTHON) -m ruff check . --fix

.PHONY: style/dapperdata
style/dapperdata:
	$(PYTHON) -m dapperdata.cli pretty . --no-dry-run

.PHONY: style/tomlsort
style/tomlsort:
	$(PYTHON_ENV) toml-sort $$(find . -name "*.toml") -i

#
# Testing
#
.PHONY: test
test: poetry.lock test/all

.PHONY: test/all
test/all: test/pytest test/ruff test/black test/mypy test/dapperdata test/tomlsort

.PHONY: test/pytest
test/pytest:
	$(PYTHON) -m pytest --cov=./${PACKAGE_SLUG} --cov-report=term-missing test

.PHONY: test/pytest-loud
test/pytest-loud:
	$(PYTHON) -m pytest -s --cov=./${PACKAGE_SLUG} --cov-report=term-missing test

.PHONY: test/ruff
test/ruff:
	$(PYTHON) -m ruff check

.PHONY: test/black
test/black:
	$(PYTHON) -m ruff format . --check

.PHONY: test/mypy
test/mypy:
	$(PYTHON) -m mypy ${PACKAGE_SLUG}

.PHONY: test/dapperdata
test/dapperdata:
	$(PYTHON) -m dapperdata.cli pretty .

.PHONY: test/tomlsort
test/tomlsort:
	$(PYTHON_ENV) toml-sort $$(find . -name "*.toml") --check

#
# Dependencies
#
.PHONY: rebuild_dependencies
rebuild_dependencies:
	poetry update

#
# Packaging
#
.PHONY: build
build: poetry.lock
	poetry build
