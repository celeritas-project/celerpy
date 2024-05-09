PACKAGE_SLUG=celerpy
ifdef CI
	PYENV_TARGET:=
	PYENV_PYTHON=python
	PYTHON_VERSION:=$(shell $(PYENV_PYTHON) --version|cut -d" " -f2)
else
	PYENV_TARGET:=pyenv
	PYENV_PYTHON:=pyenv exec python
	PYTHON_VERSION:=$(shell cat .python-version)
endif

ifeq ($(USE_SYSTEM_PYTHON), true)
	PYTHON_PACKAGE_PATH:=$(shell $(PYENV_PYTHON) -c "import sys; print(sys.path[-1])")
	PYTHON_ENV:=
	VENV_TARGET:=
else
	PYTHON_SHORT_VERSION:=$(shell echo $(PYTHON_VERSION) | grep -o '[0-9].[0-9]*')
	PYTHON_PACKAGE_PATH:=.venv/lib/python$(PYTHON_SHORT_VERSION)/site-packages
	PYTHON_ENV:=  . .venv/bin/activate &&
	VENV_TARGET:= .venv
endif

PYTHON:=$(PYTHON_ENV) python

# Used to confirm that pip has run at least once
BUILD_DIR:=$(PYTHON_PACKAGE_PATH)/build

.PHONY: all
all: $(PYENV_TARGET) $(BUILD_DIR)

.PHONY: install
install: $(PYENV_TARGET) $(VENV_TARGET) pip

.PHONY: pyenv
pyenv:
	pyenv install --skip-existing $(PYTHON_VERSION)

.venv:
	$(PYENV_PYTHON) -m venv .venv

.PHONY: pip
pip: $(VENV_TARGET)
	$(PYTHON) -m pip install -e .[dev]

$(BUILD_DIR): $(VENV_TARGET)
	$(PYTHON) -m pip install -e .[dev]

.PHONY: pre-commit
pre-commit: $(BUILD_DIR)
	$(PYTHON_ENV) pre-commit install

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
test: $(BUILD_DIR) test/all

.PHONY: test/all
test/all: test/pytest test/ruff test/black test/mypy test/dapperdata test/tomlsort

.PHONY: test/pytest
test/pytest:
	$(PYTHON) -m pytest --cov=./${PACKAGE_SLUG} --cov-report=term-missing tests

.PHONY: test/pytest-loud
test/pytest/loud:
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

requirements.txt: $(BUILD_DIR) pyproject.toml
	$(PYTHON) -m uv pip compile --upgrade --output-file=requirements.txt pyproject.toml

requirements-dev.txt: $(BUILD_DIR) pyproject.toml
	$(PYTHON) -m uv pip compile --upgrade --output-file=requirements-dev.txt --extra=dev pyproject.toml

#
# Packaging
#
.PHONY: build
build: $(BUILD_DIR)
	$(PYTHON) -m build
