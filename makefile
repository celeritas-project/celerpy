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
# Testing
#
.PHONY: test
test: poetry.lock test/all

.PHONY: test/all
test/all: test/pytest-cov test/mypy

.PHONY: test/pytest
test/pytest:
	$(PYTHON) -m pytest test

.PHONY: test/pytest-cov
test/pytest-cov:
	$(PYTHON) -m pytest --cov=./${PACKAGE_SLUG} --cov-report=term-missing test

.PHONY: test/mypy
test/mypy:
	$(PYTHON) -m mypy ${PACKAGE_SLUG}

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
