# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from celerpy.settings import settings
from celerpy.process import Process, communicate

settings.prefix_path = Path(__file__).parent / "mock-prefix"


def test_manual():
    p = Process("mock-process")
    result = communicate("hello", p)
    assert result == "success"
    result = communicate(["foo", "bar"], p)
    assert result == ["success", ["foo", "bar"]]
    result = communicate(None, p)
    assert result == "closing"
    p.wait(timeout=0.5)


def test_context():
    with Process("mock-process") as p:
        result = communicate("hello", p)
        assert result == "success"
        result = communicate(["foo", "bar"], p)
        assert result == ["success", ["foo", "bar"]]
        # NOTE: we don't explicitly tell the process to exit cleanly, so
        # when `input()` gets an EOFError due to the stdin pipe closing, the
        # process tries to write "closing" to `stdout`, but that pipe has
        # already been closed


def test_abort():
    with Process("mock-process") as p:
        result = communicate("hello", p)
        assert result == "success"
        result = communicate("abort", p)
        assert result is None


def test_abort2():
    with Process("mock-process") as p:
        result = communicate("hello", p)
        assert result == "success"
        p.terminate()
        result = communicate("terminating", p)
