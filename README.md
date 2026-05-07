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

Development is a little weird if you're not used to modern python projects,
especially because [python development and packaging evolves so
quickly](https://dev.to/farcellier/i-migrate-to-poetry-in-2023-am-i-right--115).
To isolate the development environment, this project uses
[Poetry](https://python-poetry.org/) to manage dependencies, virtual
environments, and lockfiles.

## Setting up

External dependencies (easily installed through [Homebrew](https://brew.sh/) or
another package manager):
- [Poetry](https://python-poetry.org/)
- Python 3.11 or newer

After cloning the repository, run `make pre-commit` to:
- Create and/or update the Poetry-managed virtual environment
- Install all project and development dependencies from `poetry.lock`
- Install pre-commit hooks.

If you have multiple Python versions installed, you can select one explicitly
for the project:
```console
$ poetry env use python3.11
```

## Testing and committing

At this point you can modify the python code and run tests *without* having to
reinstall the dependencies, and every `git commit` will run the tests
automatically. (Use `git commit --no-verify` to disable.)

The makefile specifies a few useful targets:
- `style`: apply style fixups to all the python files in development
- `test`: run tests
- `install`: install/update dependencies with Poetry
- `rebuild_dependencies`: update dependencies and refresh `poetry.lock`

You can also run tools directly through Poetry. For example, to run a single
python test function from a single python test, with verbose output and sending
stdout/stderr to the console, run:
```console
$ poetry run pytest -vv -s test/test_process.py -k test_context
```
