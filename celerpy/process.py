# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Manage a Celeritas process asynchronously with communication."""

import os
import subprocess
from typing import Optional, TypeVar
from pydantic import BaseModel

from .settings import settings

# TODO: from signal import SIGINT, SIGTERM


def communicate(process, line: str) -> Optional[str]:
    """Write a line and read a line of response.

    For this to work, the child application *must* write a single line of
    text, ending in a newline, with nothing else, and flush immediately
    afterward.

    If the file has already closed, this will return None.

    .. warning::
       This method is susceptible to deadlock... so be careful!
    """
    assert not line.endswith("\n")
    stdin = process.stdin
    stdout = process.stdout
    try:
        stdin.write(line)
        stdin.write("\n")
        stdin.flush()
        return stdout.readline()
    except BrokenPipeError:
        return None


M = TypeVar("M", bound=BaseModel)


def communicate_model(process, model: BaseModel, expected_cls: type[M]) -> M:
    """Communicate model to/from a process using JSON lines."""
    result = communicate(process, model.model_dump_json())
    if not result:
        raise RuntimeError("Missing output from process")
    return expected_cls.model_validate_json(result)


def launch(executable: str, *, env=None, **kwargs):
    """Set up and launch a Celeritas process."""
    # Set up environment variables
    if env is None:
        env = os.environ.copy()
    for attr in ["color"]:
        key = "CELER_" + attr.upper()
        value = getattr(settings, attr)
        if isinstance(value, bool):
            # Set to 1 or blank
            value = "1" if value else ""
        env[key] = value

    # Create child process, which implicitly keeps a copy of the file
    # descriptors
    if settings.prefix_path is None:
        raise RuntimeError("Celeritas prefix path is not set")
    return subprocess.Popen(
        [settings.prefix_path / "bin" / executable, "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        bufsize=1,  # buffer by line
        text=True,
        env=env,
        **kwargs,
    )
