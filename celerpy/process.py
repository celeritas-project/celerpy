# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Manage a Celeritas process asynchronously with communication."""

import contextlib
import os
from signal import SIGINT, SIGKILL, SIGTERM
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Optional, TypeVar

from pydantic import BaseModel, ValidationError

from . import settings
from .model.output import ExceptionDump

M = TypeVar("M", bound=BaseModel)
P = TypeVar("P", bound=Popen)

_settings_env = {
    "profiling": "CELER_ENABLE_PROFILING",
}

for _attr, _ in settings.settings:
    if _attr.startswith("g4"):
        _settings_env[_attr] = _attr.upper()


def settings_to_env() -> dict[str, str]:
    """Convert settings to environment variables."""
    env = {}
    for attr, value in settings.settings:
        if value is None:
            continue
        try:
            key = _settings_env[attr]
        except KeyError:
            key = "CELER_" + attr.upper()
        env[key] = str(value)
    return env


def launch(executable: str, *, env=None, **kwargs) -> Popen:
    """Set up and launch a Celeritas process with stdin/stdout pipes."""
    # Set up environment variables
    if env is None:
        env = os.environ.copy()
    env.update(settings_to_env())

    # Create child process, which implicitly keeps a copy of the file
    # descriptors
    prefix_path = settings.settings.prefix_path
    if prefix_path is None:
        raise RuntimeError("Celeritas prefix path is not set")
    return Popen(
        [prefix_path / "bin" / executable, "-"],
        stdin=PIPE,
        stdout=PIPE,
        bufsize=1,  # buffer by line
        text=True,
        env=env,
        **kwargs,
    )


def close(process: P, *, timeout: float = 0.1):
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
    with contextlib.suppress(BrokenPipeError):
        if not process.stdin.closed:
            process.stdin.write(line)
            process.stdin.write("\n")
            process.stdin.flush()
        if not process.stdout.closed:
            return process.stdout.readline()

    return None


class CeleritasError(Exception):
    """Error sent from Celeritas C++ encoded as a JSON line."""

    def __init__(self, e: ExceptionDump):
        self.err = e

    def __str__(self):
        return str(self.err)


def communicate_model(process: P, model: BaseModel, expected_cls: type[M]) -> M:
    """Communicate model to/from a process using JSON lines."""
    result = communicate(process, model.model_dump_json())
    if not result:
        if process.poll() is not None:
            raise RuntimeError("Process exited with code", process.returncode)
        raise RuntimeError("Missing output from process")
    try:
        return expected_cls.model_validate_json(result)
    except ValidationError:
        # Try loading as an exception
        try:
            err = ExceptionDump.model_validate_json(result)
        except ValidationError:
            pass
        else:
            raise CeleritasError(err) from None

        raise
