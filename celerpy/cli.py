from typing import Optional

import typer
from typing_extensions import Annotated

from .settings import settings

app = typer.Typer()


def print_version(value: bool):
    if value:
        from . import _version

        typer.echo(f"{settings.project_name} {_version.version}")
        raise typer.Exit()


@app.command()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=print_version, is_eager=True),
    ] = None,
):
    raise NotImplementedError("to do!")


if __name__ == "__main__":
    app()
