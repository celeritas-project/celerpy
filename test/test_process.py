# Copyright 2024 UT-Battelle, LLC, and other Celeritas developers.
# See the top-level LICENSE file for details.
# SPDX-License-Identifier: Apache-2.0

import json
import signal
from pathlib import Path

from celerpy.process import close, communicate, launch
from celerpy.settings import settings

settings.prefix_path = Path(__file__).parent / "mock-prefix"


def communicate_json(process, inp):
    out = communicate(process, json.dumps(inp))
    if out:
        return json.loads(out)
    return None


def test_manual():
    p = launch("mock-process")
    result = communicate_json(p, "hello")
    assert result == "success"
    result = communicate_json(p, ["foo", "bar"])
    assert result == ["success", ["foo", "bar"]]
    result = communicate_json(p, None)
    assert result == "closing"
    p.wait(timeout=5.0)  # should be instantaneous
    p.stdin.close()
    p.stdout.close()
    assert p.returncode == 0
    del p


def test_context():
    with launch("mock-process") as p:
        result = communicate_json(p, "hello")
        assert result == "success"
        result = communicate_json(p, ["foo", "bar"])
        assert result == ["success", ["foo", "bar"]]
        print("closing process")
        # NOTE: we don't explicitly tell the process to exit cleanly, so
        # when `input()` gets an EOFError due to the stdin pipe closing, the
        # process tries to write "closing" to `stdout`, but that pipe has
        # already been closed. I guess that also causes a BrokenPipeError in
        # the attached pipe in this process.
    print("closed process")


def test_close():
    with launch("mock-process") as p:
        result = communicate_json(p, "hello")
        assert result == "success"
        result = close(p, timeout=0.25)
        assert p.returncode == signal.SIGINT
        assert result.strip() == json.dumps("terminating")

    print("closed process")


def test_abort():
    with launch("mock-process") as p:
        result = communicate_json(p, "hello")
        assert result == "success"
        result = communicate_json(p, "abort")
        assert result is None


def test_abort2():
    with launch("mock-process") as p:
        result = communicate_json(p, "hello")
        assert result == "success"
        p.terminate()
        result = communicate_json(p, "terminating")
