> **Warning**
This repository is experimental and bare-bones at the moment. It's not ready
for general use, but discussions and contributions are welcome!

# Celeritas Python interface

You can pronounce this package like "slurpee," or really any other way you
want. This `celerpy` package will be the Python-based front end to the
[Celeritas](https://github.com/celeritas-project/celeritas) binary codes and
include a user-friendly execution interface, visualization components, and
postprocessing utilities.

# Development

To isolate the development environment, this project uses
[Poetry](https://python-poetry.org/) to manage dependencies, virtual
environments, and lockfiles. A persistent development+CI environment is encoded
into the distributed `poetry.lock` file. A simple `makefile` is included to
configure and run for those not familiar with a Poetry envirnment workflow.

## Setting up the first time

Install Poetry using [Homebrew](https://brew.sh/) or [pipx](https://pipx.pypa.io/stable/how-to/install-pipx/).

After cloning the celerpy repository and installing poetry, run `make setup` to:
- install all project and development dependencies from `poetry.lock`, and
- install pre-commit hooks.

## Development and testing

Activating the poetry environment will load the python version and all development dependencies. It is faster than manually invoking `poetry run` or using the included makefile.

```console
$ eval $(poetry env activate)
$ pytest test/
$ mypy celerpy
$ poetry run pytest -vv -s test/test_process.py -k test_context
```

## Pre-commit hooks

Style and linting should be performed automatically at every `git commit` after you run `make pre-commit`. They can also be invoked manually with `pre-commit run`. Use `git commit --no-verify` to disable temporarily for a particular commit. Pull requests automatically have their style checked and fixed via `pre-commit.ci`.

## Release/versioning

Not yet implemented:
