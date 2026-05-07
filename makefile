PACKAGE_SLUG=celerpy
ifdef CI
	PYENV_TARGET:=
	PYTHON_VERSION:=$(shell python --version|cut -d" " -f2)
else
	PYENV_TARGET:=pyenv
	PYTHON_VERSION:=$(shell cat .python-version)
endif

PYTHON:=poetry run python
PYTHON_ENV:=poetry run

.PHONY: all
all: $(PYENV_TARGET) poetry.lock

.PHONY: install
install: $(PYENV_TARGET) poetry-install

.PHONY: pyenv
pyenv:
	pyenv install --skip-existing $(PYTHON_VERSION)

.PHONY: poetry-install
poetry-install:
	poetry install

poetry.lock: pyproject.toml
	poetry install

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
	$(PYTHON_ENV) toml-sort $$(find . -not -path "./.venv/*" -name "*.toml") -i

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
	$(PYTHON_ENV) toml-sort $$(find . -not -path "./.venv/*" -name "*.toml") --check

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
