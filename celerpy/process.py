# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Manage a Celeritas process asynchronously with communication."""

import json
import os
import subprocess

from .settings import settings

# TODO: from signal import SIGINT, SIGTERM


def dump_json_line(obj, file):
    """Write a single line of JSON, a newline, and flush."""
    file.write(json.dumps(obj))
    file.write("\n")
    file.flush()


def communicate(obj, process):
    """Write a line of JSON and read a line of response.

    For this to work, the child application *must* write a single line of
    JSON formatted text, with nothing else, ending in a newline, and flush
    immediately afterward.

    If the file has already closed, this will return None.

    .. warning::
       This method is susceptible to deadlock... so be careful
    """
    try:
        dump_json_line(obj, process.stdin)
        line = process.stdout.readline()
    except BrokenPipeError:
        return None
    return json.loads(line) if line else None


class Process(subprocess.Popen):
    """Launch and manage a Celeritas process."""

    def __init__(self, executable, *, env=None, **kwargs):
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
        super().__init__(
            [settings.prefix_path / "bin" / executable, "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=1,  # buffer by line
            text=True,
            env=env,
            **kwargs,
        )
