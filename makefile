SHELL := /bin/bash
PACKAGE_SLUG=celerpy
ifdef CI
	PYTHON_PYENV :=
	PYTHON_VERSION := $(shell python --version|cut -d" " -f2)
else
	PYTHON_PYENV := pyenv
	PYTHON_VERSION := $(shell cat .python-version)
endif
PYTHON_SHORT_VERSION := $(shell echo $(PYTHON_VERSION) | grep -o '[0-9].[0-9]*')

ifeq ($(USE_SYSTEM_PYTHON), true)
	PYTHON_PACKAGE_PATH:=$(shell python -c "import sys; print(sys.path[-1])")
	PYTHON_ENV :=
	PYTHON := python
	PYTHON_VENV :=
else
	PYTHON_PACKAGE_PATH:=.venv/lib/python$(PYTHON_SHORT_VERSION)/site-packages
	PYTHON_ENV :=  . .venv/bin/activate &&
	PYTHON := . .venv/bin/activate && python
	PYTHON_VENV := .venv
endif

# Used to confirm that pip has run at least once
PACKAGE_CHECK:=$(PYTHON_PACKAGE_PATH)/build
PYTHON_DEPS := $(PACKAGE_CHECK)


.PHONY: all
all: $(PACKAGE_CHECK)

.PHONY: install
install: $(PYTHON_PYENV) $(PYTHON_VENV) pip

.venv:
	python -m venv .venv

.PHONY: pyenv
pyenv:
	pyenv install --skip-existing $(PYTHON_VERSION)

.PHONY: pip
pip: $(PYTHON_VENV)
	$(PYTHON) -m pip install -e .[dev]

$(PACKAGE_CHECK): $(PYTHON_VENV)
	$(PYTHON) -m pip install -e .[dev]

.PHONY: pre-commit
pre-commit:
	pre-commit install

#
# Formatting
#
.PHONY: style
style: style/ruff style/black style/dapperdata style/tomlsort

.PHONY: style/ruff
style/ruff:
	$(PYTHON) -m ruff check . --fix

.PHONY: style/black
style/black:
	$(PYTHON) -m ruff format .

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
test: install test/all

.PHONY: test/all
test/all: test/pytest test/ruff test/black test/mypy test/dapperdata test/tomlsort

.PHONY: test/pytest
pytest:
	$(PYTHON) -m pytest --cov=./${PACKAGE_SLUG} --cov-report=term-missing tests

.PHONY: test/pytest-loud
pytest/loud:
	$(PYTHON) -m pytest -s --cov=./${PACKAGE_SLUG} --cov-report=term-missing tests

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
	$(PYTHON) -m uv pip compile --output-file=requirements.txt pyproject.toml
	$(PYTHON) -m uv pip compile --output-file=requirements-dev.txt --extra=dev pyproject.toml

.PHONY: dependencies
dependencies: requirements.txt requirements-dev.txt

requirements.txt: $(PACKAGE_CHECK) pyproject.toml
	$(PYTHON) -m uv pip compile --upgrade --output-file=requirements.txt pyproject.toml

requirements-dev.txt: $(PACKAGE_CHECK) pyproject.toml
	$(PYTHON) -m uv pip compile --upgrade --output-file=requirements-dev.txt --extra=dev pyproject.toml



#
# Packaging
#

.PHONY: build
build: $(PACKAGE_CHECK)
	$(PYTHON) -m build
