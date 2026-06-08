PACKAGE_SLUG=celerpy
RUN:=poetry run

.PHONY: all
all: poetry.lock

poetry.lock: pyproject.toml
	poetry lock

#
# Development
#
.PHONY: dependencies
dependencies: poetry.lock
	poetry install --with=dev --with=test --no-root

.PHONY: test-dependencies
test-dependencies: poetry.lock
	poetry install --without=dev --with=test --no-root

.PHONY: pre-commit
pre-commit: dependencies
	$(RUN) pre-commit install

.PHONY: setup
setup: pre-commit

.PHONY: install
install:
	poetry install

#
# Testing
#
.PHONY: test
test: test/pytest test/mypy

.PHONY: test/pytest
test/pytest: test-dependencies
	$(RUN) python -m pytest test/

.PHONY: test/pytest-cov
test/pytest-cov: test-dependencies
	$(RUN) python -m pytest --cov=./${PACKAGE_SLUG} --cov-report=term-missing test/

.PHONY: test/mypy
test/mypy: test-dependencies
	$(RUN) python -m mypy ${PACKAGE_SLUG}

#
# Packaging
#
.PHONY: build
build: poetry.lock
	poetry build
