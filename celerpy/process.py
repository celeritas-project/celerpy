# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0
"""Manage a Celeritas process asynchronously with communication."""

import json
import os
import subprocess

from .settings import settings

# TODO: from signal import SIGINT, SIGTERM


class Process:
    """Send data to and from a Celeritas 'JSON lines'-based process.

    TODO: https://stackoverflow.com/questions/57313023/can-asyncio-subprocess-be-used-with-contextmanager
    """

    def __init__(self, executable_name, *, env=None):
        (child_stdin, send_stdin) = os.pipe()  # for parent -> child writes
        (recv_stdout, child_stdout) = os.pipe()  # for child -> parent writes

        # Buffer output line by line
        self.outfile = os.fdopen(send_stdin, "w", buffering=1)
        self.infile = os.fdopen(recv_stdout)

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
        self.child = subprocess.Popen(
            [settings.prefix_path / "bin" / executable_name, "-"],
            stdin=child_stdin,
            stdout=child_stdout,
            env=env,
        )

        # Close the descriptors in this process (child still keeps them)
        os.close(child_stdin)
        os.close(child_stdout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def communicate(self, obj):
        """Write a line of JSON and read a response."""
        print("Writing", repr(obj), "...")
        self.outfile.write(json.dumps(obj))
        self.outfile.write("\n")
        self.outfile.flush()
        print("...flushed")
        if self.child.poll():
            print("waiting...")
            return self.child.wait()
        print("reading line...")
        line = self.infile.readline()
        return json.loads(line) if line else None

    def _hard_close(self):
        self.outfile.close()
        self.infile.close()
        if not self.child.poll():
            print("terminating...")
            self.child.terminate()

    def close(self):
        try:
            if not self.child.poll():
                return self.communicate(None)
        finally:
            self._hard_close()
