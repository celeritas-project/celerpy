# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Manage a Celeritas process asynchronously with communication."""

import os
from subprocess import Popen, PIPE, TimeoutExpired
from typing import Optional, TypeVar
from pydantic import BaseModel, ValidationError

from .settings import settings

from signal import SIGINT, SIGTERM, SIGKILL


M = TypeVar("M", bound=BaseModel)
P = TypeVar("P", bound=Popen)


def launch(executable: str, *, env=None, **kwargs):
    """Set up and launch a Celeritas process with stdin/stdout pipes."""
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
    return Popen(
        [settings.prefix_path / "bin" / executable, "-"],
        stdin=PIPE,
        stdout=PIPE,
        bufsize=1,  # buffer by line
        text=True,
        env=env,
        **kwargs,
    )


def close(process: P, *, timeout: Optional[float] = 0.1):
    """Cleanly close a process."""
    if process.poll() is None:
        for s in [SIGINT, SIGTERM, SIGKILL]:
            process.send_signal(s)
            try:
                if process.wait(timeout=timeout) is not None:
                    break
            except TimeoutExpired:
                continue
    (out, _) = process.communicate()
    if process.stdin:
        process.stdin.close()
    if process.stdout:
        process.stdout.close()
    return out


def communicate(process: P, line: str) -> Optional[str]:
    """Write a line and read a line of response.

    For this to work, the child application *must* write a single line of
    text, ending in a newline, with nothing else, and flush immediately
    afterward.

    If the file has already closed, this will return None.

    .. warning::
       This method is susceptible to deadlock... so be careful!
    """
    assert not line.endswith("\n")
    assert process.stdin and process.stdout
    try:
        if not process.stdin.closed:
            process.stdin.write(line)
            process.stdin.write("\n")
            process.stdin.flush()
        if not process.stdout.closed:
            return process.stdout.readline()
    except BrokenPipeError:
        pass

    return None


def communicate_model(process: P, model: BaseModel, expected_cls: type[M]) -> M:
    """Communicate model to/from a process using JSON lines."""
    result = communicate(process, model.model_dump_json())
    if not result:
        raise RuntimeError("Missing output from process")
    try:
        return expected_cls.model_validate_json(result)
    except ValidationError:
        raise RuntimeError(
            f"Failed to validate code output as {expected_cls!r}: {result}"
        )
