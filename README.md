> **Warning**
This repository is experimental and bare-bones at the moment. It's not ready
for use, but discussions and contributions are welcome!

# Celeritas Python interface

You can pronounce this package like "slurpee," or really any other way you
want. This `celerpy` package will be the Python-based front end to the
[Celeritas](https://github.com/celeritas-project/celeritas) binary codes and
include a user-friendly execution interface, visualization components, and
postprocessing utilities.

# Development

Development is a little weird if you're not used to modern python projects,
especially because [python development and packaging evolves so
quickly](https://dev.to/farcellier/i-migrate-to-poetry-in-2023-am-i-right--115).
To isolate the development environment, `pyenv` and `pip`
install a toolchain locally.

## Setting up

External dependencies (easily installed through [Homebrew](https://brew.sh/) or
another package manager):
- [pyenv](https://github.com/pyenv/pyenv), which will install its own python versions in an isolated environment

After cloning the repository, run `make pre-commit` to:
- Install the development version of python specified in `.python-version` to
  your `pyenv` prefix (default: `~/.pyenv`, configurable with the `PYENV_ROOT`
  variable)
- Set up a virtual environment in `.venv` that will contain all the development
  dependencies, including a `celerpy` symlink in its environment that will
  point to your working copy
- Install pre-commit hooks that use the tools just installed in your virtual
  environment.

## Testing and committing

At this point you can modify the python code and run tests *without* having to
reinstall the dependencies, and every `git commit` will run the tests
automatically. (Use `git commit --no-verify` to disable.)

The makefile specifies a few useful targets:
- `style`: apply style fixups to all the python files in development
- `test`: run tests
- `pip`: reinstall all the dependencies in your virtual environment
- `rebuild_dependencies`: update the `requirements` file if you add a new
  dependency to `pyproject.toml`
