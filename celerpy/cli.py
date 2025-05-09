# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
from typing import Annotated, Optional

import typer
from pydantic import ValidationError
from rich import print as rprint

app = typer.Typer()


def load_settings():
    try:
        from .settings import settings
    except ValidationError as e:
        rprint("[bold red]Failed[/bold red]", e)
        raise typer.Exit() from None

    return settings


def print_version(value: bool):
    if value:
        from . import _version

        typer.echo(_version.version)
        raise typer.Exit()


@app.command()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=print_version, is_eager=True),
    ] = None,
):
    rprint(load_settings().model_dump())


if __name__ == "__main__":
    app()
